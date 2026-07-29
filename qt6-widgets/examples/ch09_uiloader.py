"""Qt Designer で作った .ui を使う（方法 2: 実行時に QUiLoader で読み込む）。

変換の手間がない代わりに、
  ・エディタの補完が効かない（属性がその場で生えるため）
  ・.ui の配布が必要
  ・load() が返すのは新しいウィジェットで、self ではない
という違いがある。

実行:  python ch09_uiloader.py
"""

import sys
from pathlib import Path

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication

app = QApplication(sys.argv)

loader = QUiLoader()
ui_file = Path(__file__).parent / "ch09_form.ui"
form = loader.load(ui_file)      # 戻り値が画面そのもの
if form is None:
    raise SystemExit(f"読み込みに失敗しました: {loader.errorString()}")

# 子ウィジェットは objectName で属性としてたどれる。
form.submitButton.setEnabled(False)
form.agreeCheck.toggled.connect(form.submitButton.setEnabled)
form.submitButton.clicked.connect(
    lambda: form.resultLabel.setText(
        f"{form.nameEdit.text() or 'ななし'} さんを"
        f"「{form.planCombo.currentText()}」で受け付けました"
    )
)

form.show()

sys.exit(app.exec())
