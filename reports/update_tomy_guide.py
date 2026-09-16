from pathlib import Path
p=Path('app/ui/assistant.py')
s=p.read_text(encoding='utf-8')
a=s.index('class MascotDialog(QDialog):')
b=s.index('\n\ndef show_assistant',a)
new='''class MascotDialog(QDialog):
    """Guía contextual de Tomy, presentada un paso a la vez."""

    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.content = HELP_CONTENT[context]
        self.step_index = 0
        self.setWindowTitle("Tomy | " + self.content["title"])
        self.setObjectName("tomyGuide")
        self.setModal(True)
        self.setFixedWidth(560)
        self.setStyleSheet("""
            QDialog#tomyGuide { background: #F6F8FC; }
            QDialog#tomyGuide QLabel, QDialog#tomyGuide QPushButton { font-family: 'Segoe UI'; }
            QFrame#guideHero { background: #103D6C; border-radius: 14px; }
            QLabel#guideEyebrow { color: #F4CE67; font-size: 11px; font-weight: 700; }
            QLabel#guideTitle { color: white; font-size: 22px; font-weight: 700; }
            QLabel#guideIntro { color: #42566D; font-size: 14px; }
            QFrame#guideStep { background: white; border: 1px solid #DFE7F1; border-radius: 12px; }
            QLabel#guideCounter { color: #0B63BA; font-size: 11px; font-weight: 700; }
            QLabel#guideInstruction { color: #19334F; font-size: 17px; font-weight: 600; }
            QLabel#guideTip { color: #6C5420; background: #FFF6DD; padding: 14px; border-radius: 10px; font-size: 12px; }
            QPushButton { border: 1px solid #CCD9E8; background: white; color: #24496E; border-radius: 8px; padding: 10px 16px; font-size: 12px; }
            QPushButton:hover { background: #E8F1FC; }
            QPushButton:disabled { color: #98A4B4; background: #F0F3F7; }
            QPushButton#guideNext { background: #0B63CE; color: white; border: none; font-weight: 700; }
            QPushButton#guideNext:hover { background: #094FAD; }
        """)
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(18)
        hero = QFrame(objectName="guideHero")
        heading = QHBoxLayout(hero)
        heading.setContentsMargins(18, 18, 18, 18)
        avatar = QLabel()
        avatar.setPixmap(draw_dog_face(88))
        heading.addWidget(avatar)
        text = QVBoxLayout()
        text.addWidget(QLabel("SOY TOMY, TU GUÍA", objectName="guideEyebrow"))
        title = QLabel(self.content["title"], objectName="guideTitle")
        title.setWordWrap(True)
        text.addWidget(title)
        heading.addLayout(text, 1)
        root.addWidget(hero)
        intro = QLabel(self.content["what"], objectName="guideIntro")
        intro.setWordWrap(True)
        root.addWidget(intro)
        card = QFrame(objectName="guideStep")
        step_layout = QVBoxLayout(card)
        step_layout.setContentsMargins(20, 18, 20, 18)
        step_layout.setSpacing(12)
        self.counter = QLabel(objectName="guideCounter")
        self.instruction = QLabel(objectName="guideInstruction")
        self.instruction.setWordWrap(True)
        self.instruction.setMinimumHeight(80)
        step_layout.addWidget(self.counter)
        step_layout.addWidget(self.instruction)
        root.addWidget(card)
        tip = QLabel("CONSEJO DE TOMY\\n" + self.content["tip"], objectName="guideTip")
        tip.setWordWrap(True)
        root.addWidget(tip)
        actions = QHBoxLayout()
        close = QPushButton("Cerrar guía")
        close.clicked.connect(self.reject)
        self.previous = QPushButton("Anterior")
        self.previous.clicked.connect(self._previous_step)
        self.next_button = QPushButton(objectName="guideNext")
        self.next_button.clicked.connect(self._next_step)
        actions.addWidget(close)
        actions.addStretch()
        actions.addWidget(self.previous)
        actions.addWidget(self.next_button)
        root.addLayout(actions)
        self._update_step()

    def _update_step(self):
        import re
        steps = self.content["steps"]
        self.counter.setText(f"PASO {self.step_index + 1} DE {len(steps)}")
        self.instruction.setText(re.sub(r"^\\d+\\.\\s*", "", steps[self.step_index]))
        self.previous.setEnabled(self.step_index > 0)
        self.next_button.setText("Entendido" if self.step_index == len(steps) - 1 else "Siguiente →")

    def _previous_step(self):
        self.step_index = max(0, self.step_index - 1)
        self._update_step()

    def _next_step(self):
        if self.step_index == len(self.content["steps"]) - 1:
            self.accept()
        else:
            self.step_index += 1
            self._update_step()
'''
p.write_text(s[:a]+new+s[b:],encoding='utf-8')
