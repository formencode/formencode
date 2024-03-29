import formencode

ne = formencode.validators.NotEmpty()


def _test_builtins(func):
    def dummy(s):
        return "builtins dummy"
    import builtins
    builtins._ = dummy

    try:
        ne.to_python("")
    except formencode.api.Invalid as e:
        func(e)

    del builtins._


def test_builtins():
    def withbuiltins(e):
        assert str(e) == "builtins dummy"

    _test_builtins(withbuiltins)


def test_bultins_disabled():
    def withoutbuiltins(e):
        assert str(e) != "builtins dummy"

    ne.use_builtins_gettext = False
    _test_builtins(withoutbuiltins)


def test_state():
    class st:
        def _(self, s):
            return "state dummy"

    try:
        ne.to_python("", state=st())
    except formencode.api.Invalid as e:
        assert str(e) == "state dummy"


def _test_lang(language, notemptytext):

    formencode.api.set_stdtranslation(languages=[language])

    try:
        ne.to_python("")
    except formencode.api.Invalid as e:
        assert str(e) == notemptytext

    formencode.api.set_stdtranslation()  # set back to defaults


def test_de():
    _test_lang("de", "Bitte einen Wert eingeben")


def test_es():
    _test_lang("es", "Por favor introduzca un valor")


def test_pt_BR():
    _test_lang("pt_BR", "Por favor digite um valor")


def test_zh_TW():
    _test_lang("zh_TW", "請輸入值")


def test_sk():
    _test_lang("sk", "Zadajte hodnotu, prosím")


def test_ru():
    _test_lang("ru", "Необходимо ввести значение")


def test_sl():
    _test_lang("sl", "Prosim, izpolnite polje")


def test_pt_PT():
    _test_lang("pt_PT", "Por favor insira um valor")


def test_fr():
    _test_lang("fr", "Saisissez une valeur")


def test_nl():
    _test_lang("nl", "Voer een waarde in")


def test_pl():
    _test_lang("pl", "Proszę podać wartość")


def test_el():
    _test_lang("el", "Παρακαλούμε εισάγετε μια τιμή")


def test_zh_CN():
    _test_lang("zh_CN", "请输入一个值")


def test_cs():
    _test_lang("cs", "Prosím zadejte hodnotu")


def test_fi():
    _test_lang("fi", "Anna arvo")


def test_nb_NO():
    _test_lang("nb_NO", "Venligst fyll inn en verdi")


def test_it():
    _test_lang("it", "Inserire un dato")


def test_et():
    _test_lang("et", "Palun sisestada väärtus")


def test_lt():
    _test_lang("lt", "Prašome įvesti reikšmę")


def test_ja():
    _test_lang("ja", "入力してください")


def test_tr():
    _test_lang("tr", "Lütfen bir değer giriniz")
