from webapp2_extras import i18n


# i18n language handler
class Language:
    def __init__(self):
        pass

    @staticmethod
    def setlanguage(lang):
        i18n.get_i18n().set_locale(lang)

    @staticmethod
    def language(http):
        # Language change petition
        newLang = http.request.get('language')
        cookieLang = http.request.cookies.get('language')
        currentLang = None
        if len(newLang) > 1:
            currentLang = newLang
        else:
            if cookieLang is None or len(cookieLang) < 1:
                currentLang = 'en_US'
            else:
                currentLang = cookieLang
        http.response.set_cookie('language', currentLang, max_age=15724800) # 26 weeks in seconds
        Language.setlanguage(currentLang)
