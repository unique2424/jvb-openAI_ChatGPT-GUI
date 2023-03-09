from PyQt5 import QtCore, QtWidgets, uic, QtGui
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import QPropertyAnimation, QRect
import pyperclip, openai, pyttsx3, webbrowser

class Main(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = uic.loadUi('openAiGUI.ui',self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        self.thread={}

        self.wait.hide()
        self.settingsContainer.setGeometry(483, 0, 349, 501)
        self.loading_gif = QMovie("assets/loading.gif")
        self.wait.setMovie(self.loading_gif)
        self.loading_gif.start()

        self.settingsContainer.setGeometry(483, 0, 349, 501)
        self.stackedWidget.setCurrentIndex(0)

        self.quitBtn.clicked.connect(lambda: quit())
        self.frame_2.mouseMoveEvent = self.MoveWindow

        self.copyBtn.clicked.connect(self.copyText)
        self.submit.clicked.connect(lambda: self.start_ai(tr=1))

        #Hover Texts
        self.modelText.setToolTip(self.hoverText('model'))
        self.tempText.setToolTip(self.hoverText('temp'))
        self.maxLText.setToolTip(self.hoverText('maxL'))
        self.topPText.setToolTip(self.hoverText('topP'))
        self.freqText.setToolTip(self.hoverText('freq'))
        self.presText.setToolTip(self.hoverText('pres'))
        self.copyBtn.setToolTip(self.hoverText('copy'))
        self.settingsBtn.setToolTip(self.hoverText('settings'))
        self.closeBtn.setToolTip(self.hoverText('close'))
        self.saveBtn.setToolTip(self.hoverText('save'))
        self.restore.setToolTip(self.hoverText('restore'))
        self.clearBtn.setToolTip(self.hoverText('clear'))
        self.tokenCount.setToolTip(self.hoverText('token'))


        #Sliders
        self.model.currentIndexChanged.connect(lambda: self.modelName.setText(str(self.model.currentText())))
        self.temp.valueChanged.connect(self.tempSlider)
        self.maxL.valueChanged.connect(self.maxLSlider)
        self.topP.valueChanged.connect(self.topPSlider)
        self.freq.valueChanged.connect(self.freqSlider)
        self.pres.valueChanged.connect(self.presSlider)
    
        self.saveBtn.clicked.connect(self.saveConfig)
        self.setApiBtn.clicked.connect(self.saveConfig)
        self.restore.clicked.connect(self.restoreDafault)

        self.settingsBtn.clicked.connect(lambda: self.toggleSettingsContainer(True))
        self.closeBtn.clicked.connect(lambda: self.toggleSettingsContainer(False))

        self.speechBtn.clicked.connect(lambda: self.start_ai(tr=2))
        self.usrInpt.textChanged.connect(self.tokenContLabel)
        self.clearBtn.clicked.connect(self.clearPrompt)
        self.apiBtn.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.ifNoApi.clicked.connect(lambda: webbrowser.open_new_tab('https://platform.openai.com/account/api-keys'))
        self.apiInpt.textChanged.connect(self.setApiBtnLabel)
    
    def restoreDafault(self):
        model = 0
        temp  = 90
        maxL  = 2048
        topP  = 100
        freq  = 0
        pres  = 60
        best  = 0

        self.model.setCurrentIndex(model)
        self.temp.setValue(temp)
        self.maxL.setValue(maxL)
        self.topP.setValue(topP)
        self.freq.setValue(freq)
        self.pres.setValue(pres)
        self.best.setValue(best)

    def presSlider(self):
        valStr = str(f"0.{self.pres.value()}")
        
        if valStr == '0.100': val = '1'
        elif valStr == '0.0': val = '0'
        elif valStr == '0.200': val = '2'
        else: val = valStr

        self.pres_c.setText(str(val))
        
    def freqSlider(self):
        valStr = str(f"0.{self.freq.value()}")
        
        if valStr == '0.100': val = '1'
        elif valStr == '0.0': val = '0'
        elif valStr == '0.200': val = '2'
        else: val = valStr

        self.freq_c.setText(str(val))

    def topPSlider(self):
        valStr = str(f"0.{self.topP.value()}")
        
        if valStr == '0.100': val = '1'
        elif valStr == '0.0': val = '0' 
        else: val = valStr

        self.topP_c.setText(str(val))
    
    def maxLSlider(self):
        val = self.maxL.value()
        self.maxL_c.setText(str(val))

    def tempSlider(self):
        valStr = str(f"0.{self.temp.value()}")
        
        if valStr == '0.100': val = '1'
        elif valStr == '0.0': val = '0'
        else: val = valStr

        self.temp_c.setText(str(val))

    def hoverText(self, id):
        self.setStyleSheet("""QToolTip { 
                    background-color: black; 
                    color: white; 
                    border: black solid 1px
                    }""")
        if id == 'model':
            text = '''The model which will generate the completion.
Some models are suitable for natural language tasks, others specialize in code.'''
        elif id == 'temp':
            text = '''Controls randomness: Lowering results in less random completions.
As the temperature approaches zero, the model will become deterministic and repetitive.'''
        elif id == 'maxL':
            text = '''The maximum number of tokens to <b>generate</b>. Requests can use up to 2,048 or 4,000 tokens
shared between prompt and completion. The exact limit varies by model. (One token is roughly 4 characters for normal English text)'''
        elif id == 'topP':
            text = '''Controls diversity via nucleus sampling:
0.5 means half of all likelihood-weighted options are considered.'''
        elif id == 'freq':
            text = '''How much to penalize new tokens based on their existing frequency in the text so far.
Decreases the model's likelihood to repeat the same line verbatim.'''
        elif id == 'pres':
            text = '''How much to penalize new tokens based on whether they appear in the text so far
Increases the model's likelihood to talk about new topics.'''
        elif id == 'best':
            text = '''Generates multiple completions server- side, and displays only the best.
Streaming only works when set to 1. Since it acts as a multiplier on the number of completions,
this parameters can eat into your token quota very quickly - use caution!'''
        elif id == 'token':
            text = f'''Tokens'''
        elif id == 'copy':
            text = '''Copy text'''
        elif id == 'settings':
            text = '''Open Settings'''
        elif id == 'close':
            text = '''Close Settings'''
        elif id == 'save':
            text = '''Save Settings'''
        elif id == 'restore':
            text = '''Restore Dafault Settings'''
        elif id == 'clear':
            text = '''Clear'''
        return text

    def saveConfig(self):
        self.toggleSettingsContainer(False)
        self.stackedWidget.setCurrentIndex(0)

    def copyText(self):
        pyperclip.copy(str(self.aiPage.toPlainText()))
        self.copyBtn_tt.setText('text Copied.')

    def MoveWindow(self, event):
        if self.isMaximized() == False:
            self.move(self.pos() + event.globalPos() - self.clickPosition)
            self.clickPosition = event.globalPos()
            event.accept()
            pass

    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()
        pass
    
    def setApiBtnLabel(self):
        text = self.apiInpt.toPlainText()

        if text != '':
            self.setApiBtn.setText('SET')
        else:
            self.setApiBtn.setText('CLOSE')

    def toggleSettingsContainer(self, toggle):
        self.animation = QtCore.QPropertyAnimation(self.ui.settingsContainer, b"geometry")
        self.animation.setDuration(250)
        self.animation.setEasingCurve(QtCore.QEasingCurve.Type.InOutQuart)
        if toggle:
            # OPEN ANIMATION
            self.animation.setStartValue(QRect(483, 0, 349, 501))
            self.animation.setEndValue(QRect(132, 0, 349, 501)) 
        else:
            self.animation.setStartValue(QRect(132, 0, 349, 501))
            self.animation.setEndValue(QRect(483, 0, 349, 501))
        
        self.animation.start()

    def clearPrompt(self):
        self.aiPage.setPlainText('')
        self.usrInpt.setPlainText('')

    def tokenContLabel(self):
        ai  = len(self.aiPage.toPlainText().split())
        usr = len(self.usrInpt.toPlainText().split())

        count = ai + usr
        self.tokenCount.setText(str(count))

        red   = 'rgb(255, 0, 0)'
        white = 'rgb(255, 255, 255)'

        if count >= int(self.maxL_c.text()):
            color = red
        else:
            color = white
        
        self.tokenCount.setStyleSheet(f"background-color: rgba(65, 65, 65, 120); \
                                        border: none;border-radius: 8px; \
                                        color: {color}")

    def btnToggle(self, toggle):
        if toggle == False:
            self.usrInpt.setReadOnly(True)
            self.submit.setEnabled(False)
            # self.speechBtn.setEnabled(False)
            self.copyBtn.setEnabled(False)
            self.settingsBtn.setEnabled(False)
            
        elif toggle == True:
            self.usrInpt.setReadOnly(False)
            self.submit.setEnabled(True)
            # self.speechBtn.setEnabled(True)
            self.copyBtn.setEnabled(True)
            self.settingsBtn.setEnabled(True)

    def start_ai(self, tr=1):
        model  = str(self.model.currentText())
        prompt = self.usrInpt.toPlainText()
        temp   = float(self.temp_c.text())
        maxL   = int(self.maxL_c.text())
        topP   = int(self.topP_c.text())
        freq   = float(self.freq_c.text())
        pres   = float(self.pres_c.text())
        text   = self.aiPage.toPlainText()

        if self.apiInpt.toPlainText() != '':
            api = self.apiInpt.toPlainText()
        else:
            api = "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"

        if tr == 1:
            self.wait.show()
            self.aiPage.setPlainText('')
            self.tokenCount.setText(str(len(self.usrInpt.toPlainText().split())))
            self.thread[1] = ThreadClass(
                parent = None,
                index  = 1,
                model  = model,
                prompt = prompt,
                temp   = temp,
                maxL   = maxL,
                topP   = topP,
                freq   = freq,
                pres   = pres,
                text   = text,
                api    = api)

            self.thread[1].start()
            self.thread[1].aiPromptEmit.connect(self.aiPrompt)
        elif tr == 2:
            self.thread[2] = ThreadClass(
                parent = None,
                index  = 2,
                model  = model,
                prompt = prompt,
                temp   = temp,
                maxL   = maxL,
                topP   = topP,
                freq   = freq,
                pres   = pres,
                text   = text,
                api    = api)

            self.thread[2].start()
            self.thread[2].speechEmit.connect(self.speech)

        self.btnToggle(False)
    
    def speech(self, toggle):
        if toggle == True:
            icon = QtGui.QPixmap('assets/speech.png')
            self.speechBtn.setIcon(QtGui.QIcon(icon))
        else:
            icon = QtGui.QPixmap('assets/speech1.png')
            self.speechBtn.setIcon(QtGui.QIcon(icon))

        self.btnToggle(True)

    def aiPrompt(self, text):
        self.wait.hide()

        self.aiPage.setPlainText(text)

        self.btnToggle(True)
        self.tokenContLabel()

class ThreadClass(QtCore.QThread):
    aiPromptEmit = QtCore.pyqtSignal(str)
    speechEmit   = QtCore.pyqtSignal(bool)
    def __init__(
        self,
        parent = None,
        index  = 0,
        model  = 'text-davinci-003',
        prompt = '',
        temp   = 0.9,
        maxL   = 2048,
        topP   = 1,
        freq   = 0,
        pres   = 0.6,
        text   = '',
        api    = ''):

        super(ThreadClass, self).__init__(parent)
        self.index=index
        self.is_running = True

        openai.api_key = api
        
        self.model  = model
        self.prompt = prompt
        self.temp   = temp
        self.maxL   = maxL
        self.topP   = topP
        self.freq   = freq
        self.pres   = pres
        self.text   = text
    
    def openai_create(self):
        response = openai.Completion.create(
            model             = self.model,
            prompt            = self.prompt,
            temperature       = self.temp,
            max_tokens        = self.maxL,
            top_p             = self.topP,
            frequency_penalty = self.freq,
            presence_penalty  = self.pres,
            stop              = [" Human:", " AI:"])

        return response.choices[0].text
    
    def speech(self, text):
        if text != '':
            engine = pyttsx3.init()
            voices = engine.getProperty("voices")
            engine.setProperty("voice", voices[0].id)
            engine.setProperty("rate", 200)
            engine.say(text)

            engine.runAndWait()

    def run(self):
        if self.index == 1:
            try:
                text = self.openai_create().replace("\n\n", "", 1)
            except Exception as e:
                text = e
            self.aiPromptEmit.emit(str(text))

        elif self.index == 2:
            try:
                self.speechEmit.emit(False)
                self.speech(self.text)
                self.speechEmit.emit(True)
            except RuntimeError:
                pass

        
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = Main()
    mainWindow.show()
    sys.exit(app.exec_())