from enum import Enum


class ILOStatLanguage(Enum):
    en = "english",
    fr = "français",
    es = "español"


class ILOStat:
    def __init__(self, language: ILOStatLanguage):
        if not isinstance(language, ILOStatLanguage):
            raise ValueError(f"Invalid language: {
                             language}. Must be an instance of ILOStatLanguage.")
        print(language)


if __name__ == "__main__":
    ilostat = ILOStat(ILOStatLanguage.en)
