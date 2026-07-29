"""最初のウィンドウ — Qt アプリに絶対必要な 3 つの要素だけを書いたもの。

実行:  python ch02_hello.py
"""

import sys

from PySide6.QtWidgets import QApplication, QLabel

# ① アプリケーション本体。Qt の世界にひとつだけ存在する「司令塔」。
app = QApplication(sys.argv)

# ② 画面に置くもの（ウィジェット）。親を持たないウィジェットは
#    それ自体が独立したウィンドウになる。
label = QLabel("こんにちは、Qt!")
label.show()

# ③ イベントループ。ここでプログラムは「待ち」に入り、
#    ユーザーの操作を待ち受け続ける。閉じられると exec() が返る。
sys.exit(app.exec())
