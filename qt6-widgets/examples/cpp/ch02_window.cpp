// ch02_window.py と同じ画面を C++ で書いたもの。
//
// Python 版と見比べてください。呼んでいるクラスもメソッドも、まったく同じです。
// 違うのは「言語としての書き方」だけです。

#include <QApplication>
#include <QLabel>
#include <QVBoxLayout>
#include <QWidget>

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);

    // Python: window = QWidget()
    // C++ では、この場所（スタック）に置くだけで作られる。new は要らない。
    QWidget window;
    window.setWindowTitle("はじめての Qt ウィンドウ");
    window.resize(420, 180);

    // Python: layout = QVBoxLayout(window)
    // ここは new で作る。理由は、レイアウトの寿命を window に任せるため。
    QVBoxLayout *layout = new QVBoxLayout(&window);
    layout->addWidget(new QLabel("ようこそ、Qt Widgets の世界へ。"));
    layout->addWidget(new QLabel("このウィンドウは 20 行足らずで出来ています。"));

    window.show();

    // Python: sys.exit(app.exec())
    return app.exec();
}
