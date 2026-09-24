"""Assistant d'urgence IA pour l'accompagnant (Gemini via backend, ou mock)."""
import threading

from kivy.clock import Clock
from kivy.factory import Factory
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from services.gemini_assistant import FALLBACK_GUIDANCE
from utils.constants import CYAN, TEXT_DIM, WARNING
from utils.formatting import fmt_duration
from widgets.base import CardBox
from widgets.chat_bubble import ChatBubble

from . import MediScreen


class AIAssistantScreen(MediScreen):
    back_to = "emergency"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._loaded = False

    def build_ui(self):
        root = BoxLayout(orientation="vertical")
        root.add_widget(self.make_header("Assistant d'urgence"))

        self.status_card = CardBox(orientation="horizontal",
                                   size_hint_y=None, height=dp(52),
                                   spacing=dp(10))
        self.status_label = Label(text="Ambulance en route",
                                  font_size=sp(13), bold=True, color=CYAN,
                                  halign="left")
        self.status_card.add_widget(self.status_label)
        root.add_widget(self.status_card)

        self.scroll = ScrollView(do_scroll_y=True, bar_width=dp(3))
        self.chat_list = GridLayout(cols=1, spacing=dp(8), size_hint_y=None,
                                    padding=(dp(10), dp(10), dp(10), dp(10)))
        self.chat_list.bind(minimum_height=self.chat_list.setter("height"))
        self.scroll.add_widget(self.chat_list)
        root.add_widget(self.scroll)

        self.typing = Label(text="Assistant en train d'analyser...",
                            font_size=sp(11), color=TEXT_DIM, halign="left",
                            size_hint_y=None, height=dp(20),
                            padding=(dp(16), 0))
        root.add_widget(self.typing)

        input_row = BoxLayout(size_hint_y=None, height=dp(56),
                              spacing=dp(8),
                              padding=(dp(10), dp(6), dp(10), dp(6)))
        self.input = Factory.MediTextInput(
            hint_text="Décrivez la situation...")
        self.input.height = dp(44)
        send = Factory.SmallButton(text="Envoyer", size_hint_x=None,
                                   width=dp(96))
        send.height = dp(44)
        send.bind(on_release=lambda i: self._send())
        self.input.bind(on_text_validate=self._send)
        input_row.add_widget(self.input)
        input_row.add_widget(send)
        root.add_widget(input_row)
        self.add_widget(root)

    # ------------------------------------------------------------------
    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        if not self._loaded:
            self._loaded = True
            self._load_guidance()
        self.refresh()

    def refresh(self):
        em = self.state.services.emergency_manager
        text = em.ambulance_status
        if em.eta_seconds:
            text += f" — temps estimé {fmt_duration(em.eta_seconds)}"
        self.status_label.text = text

    def _context(self):
        state = self.state
        em = state.services.emergency_manager
        from services.gemini_assistant import GeminiAssistant
        return GeminiAssistant.build_context(
            state.patient, state.health_data, em.alert, em.facility,
            em.ambulance_status, em.location)

    def _add_bubble(self, who, message):
        self.chat_list.add_widget(ChatBubble(who=who, message=message))
        Clock.schedule_once(lambda dt: setattr(self.scroll, "scroll_y", 0.0),
                            0.05)

    def _load_guidance(self):
        self.typing.opacity = 1
        context = self._context()

        def work():
            guidance = None
            try:
                guidance = self.state.services.assistant.get_initial_guidance(
                    context)
            except Exception:
                guidance = None
            Clock.schedule_once(lambda dt: self._show_guidance(guidance), 0.9)

        threading.Thread(target=work, daemon=True).start()

    def _show_guidance(self, guidance):
        self.typing.opacity = 0
        if not guidance:
            self._add_bubble("ai", "Assistant IA temporairement indisponible.")
            guidance = FALLBACK_GUIDANCE
        for line in guidance:
            self._add_bubble("ai", line)

    def _send(self, *args):
        message = self.input.text.strip()
        if not message:
            return
        self.input.text = ""
        self._add_bubble("user", message)
        self.typing.opacity = 1
        context = self._context()

        def work():
            reply = None
            try:
                reply = self.state.services.assistant.chat(message, context)
            except Exception:
                reply = None
            Clock.schedule_once(lambda dt: self._show_reply(reply), 1.0)

        threading.Thread(target=work, daemon=True).start()

    def _show_reply(self, reply):
        self.typing.opacity = 0
        if not reply:
            reply = ("Assistant IA temporairement indisponible. "
                     + FALLBACK_GUIDANCE[0])
        self._add_bubble("ai", reply)
