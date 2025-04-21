class TranslationManager:
    _CURRENT_LANGUAGE = "pl"

    LANGUAGES = {
        "pl": "Polski",
        "en": "English",
        "de": "Deutsch"
    }

    TRANSLATIONS = {
        "pl": {
            "loading": "Ładowanie...",
            "error": "Błąd",
            "success": "Sukces",
            "warning": "Ostrzeżenie",
            "info": "Informacja",
            "back": "Powrót",
            "cancel": "Anuluj",
            "confirm": "Potwierdź",
            "save": "Zapisz",
            "delete": "Usuń",
            "add": "Dodaj",
            "edit": "Edytuj",
            "close": "Zamknij",
            "send": "Wyślij",
            "search": "Szukaj",

            "welcome_title": "Witaj w Zabytkowniku!",
            "welcome_subtitle": "Odkrywaj, zwiedzaj i dokumentuj swoje przygody",
            "register": "Zarejestruj się",
            "login": "Zaloguj się",
            "about_app": "O aplikacji",
            "change_theme": "Zmień motyw",
            "change_language": "Zmień język",

            "about_app_title": "O aplikacji",
            "about_app_content": "Zabytkownik to aplikacja, która pomoże Ci odkrywać, dokumentować i dzielić się swoimi wizytami w zabytkach. Zarejestruj się, aby rozpocząć swoją przygodę z historią architektury!",

            "login_title": "Logowanie",
            "username": "Nazwa użytkownika",
            "password": "Hasło",
            "login_welcome": "Witaj ponownie!",
            "login_subtitle": "Zaloguj się, aby kontynuować swoją przygodę z zabytkami",
            "no_account": "Nie masz konta?",
            "register_link": "Zarejestruj się",

            "register_title": "Rejestracja",
            "confirm_password": "Potwierdź hasło",
            "register_welcome": "Dołącz do społeczności",
            "register_subtitle": "Stwórz konto, aby odkrywać i dokumentować swoje podróże",
            "have_account": "Masz już konto?",
            "login_link": "Zaloguj się",

            "profile": "Profil",
            "logout": "Wyloguj",
            "monuments_visited": "Liczba odwiedzonych zabytków",
            "discover_more": "Odkryj więcej zabytków i zwiększ swój wynik!",
            "congrats": "Gratulacje! Jesteś prawdziwym odkrywcą zabytków!",
            "visited_monuments": "Odwiedzone zabytki",
            "no_monuments": "Nie odwiedziłeś jeszcze żadnych zabytków",
            "start_exploring": "Rozpocznij swoją przygodę odkrywania zabytków!",
            "discover": "Odkryj zabytki",
            "show_map": "Pokaż mapę odwiedzonych zabytków",
            "logout_confirm": "Czy na pewno chcesz się wylogować?",
            "logout_success": "Zostałeś wylogowany",

            "continents_title": "Wybierz kontynent",
            "welcome_user": "Witaj, {0}!",
            "select_continent": "Wybierz kontynent, który chcesz zwiedzić",
            "continent_europe": "Europa",
            "continent_asia": "Azja",
            "continent_north_america": "Ameryka Północna",
            "continent_south_america": "Ameryka Południowa",
            "continent_africa": "Afryka",
            "continent_australia": "Australia i Oceania",
            "available": "Dostępny",
            "coming_soon": "Wkrótce dostępny",
            "select": "Wybierz",

            "countries_in": "Kraje w {0}",
            "select_country": "Wybierz kraj aby zobaczyć dostępne miasta i zabytki",

            "cities_in": "Miasta w {0}",
            "select_city": "Wybierz miasto aby zobaczyć dostępne zabytki",
            "show_map": "Pokaż mapę",
            "country_map": "Mapa {0}",
            "soon_available": "będzie dostępne wkrótce!",


            "monuments_in": "Zabytki w {0}",
            "discover_monuments": "Odkryj zabytki {0}",
            "monument_details": "Szczegóły",
            "show_on_map": "Na mapie",
            "mark_visited": "Oznacz jako odwiedzony",
            "already_visited": "✓ Zabytek odwiedzony!",
            "unmark_visited": "Cofnij oznaczenie",
            "verify_photo": "Zweryfikuj przez zdjęcie",
            "description": "Opis",
            "location": "Lokalizacja",
            "see_on_google_maps": "Zobacz na Google Maps",

            "map_title": "Mapa zabytków",
            "map_subtitle": "Kliknij marker, aby zobaczyć szczegóły zabytku",
            "close_map": "Zamknij mapę",
            "available_monuments": "Dostępne zabytki:",
            "open_interactive_map": "Otwórz pełną mapę interaktywną",

            "verify_title": "Weryfikacja zabytku: {0}",
            "verification_info": "Jak działa weryfikacja?",
            "verification_description": "System analizuje zdjęcie i porównuje je z referencjami zabytku, używając zaawansowanego modelu AI. Wynik powyżej 70% przy niskim podobieństwie do innych zabytków oznacza sukces.",
            "verification_tips": "Porady dla najlepszych wyników:",
            "tip_1": "• Upewnij się, że zabytek jest wyraźnie widoczny",
            "tip_2": "• Fotografuj w dobrym oświetleniu",
            "tip_3": "• Unikaj przeszkód zasłaniających zabytek",
            "verification_instruction": "Zrób lub wybierz zdjęcie zabytku, aby zweryfikować swoją obecność.",
            "select_photo": "Wybierz zdjęcie",
            "take_photo": "Zrób zdjęcie",
            "processing": "Analizowanie zdjęcia...",
            "force_accept": "Wymuś akceptację",
            "view_profile": "Zobacz swój profil",
            "added_to_profile": "Zabytek dodany do Twojego profilu!",

            "error_loading": "Błąd podczas ładowania danych",
            "try_again": "Spróbuj ponownie",
            "refresh": "Odśwież",
            "no_monuments_found": "Nie znaleziono zabytków dla tego miasta",
            "no_data": "Brak danych",
            "select_file": "Wybierz plik JPG, JPEG lub PNG",
            "camera_unavailable": "Funkcja aparatu będzie dostępna wkrótce!",
            "error_processing": "Błąd przetwarzania pliku"
        },

        "en": {
            "loading": "Loading...",
            "error": "Error",
            "success": "Success",
            "warning": "Warning",
            "info": "Information",
            "back": "Back",
            "cancel": "Cancel",
            "confirm": "Confirm",
            "save": "Save",
            "delete": "Delete",
            "add": "Add",
            "edit": "Edit",
            "close": "Close",
            "send": "Send",
            "search": "Search",

            "welcome_title": "Welcome to Zabytkownik!",
            "welcome_subtitle": "Explore, visit and document your adventures",
            "register": "Register",
            "login": "Log in",
            "about_app": "About app",
            "change_theme": "Change theme",
            "change_language": "Change language",

            "about_app_title": "About app",
            "about_app_content": "Zabytkownik is an application that will help you discover, document and share your visits to monuments. Register to start your adventure with architectural history!",

            "login_title": "Login",
            "username": "Username",
            "password": "Password",
            "login_welcome": "Welcome back!",
            "login_subtitle": "Log in to continue your adventure with monuments",
            "no_account": "Don't have an account?",
            "register_link": "Register",

            "register_title": "Registration",
            "confirm_password": "Confirm password",
            "register_welcome": "Join the community",
            "register_subtitle": "Create an account to discover and document your travels",
            "have_account": "Already have an account?",
            "login_link": "Log in",

            "profile": "Profile",
            "logout": "Logout",
            "monuments_visited": "Number of monuments visited",
            "discover_more": "Discover more monuments and increase your score!",
            "congrats": "Congratulations! You are a true monument explorer!",
            "visited_monuments": "Visited monuments",
            "no_monuments": "You haven't visited any monuments yet",
            "start_exploring": "Start your monument exploring adventure!",
            "discover": "Discover monuments",
            "show_map": "Show visited monuments map",
            "logout_confirm": "Are you sure you want to log out?",
            "logout_success": "You have been logged out",

            "continents_title": "Select continent",
            "welcome_user": "Welcome, {0}!",
            "select_continent": "Select a continent you want to explore",
            "continent_europe": "Europe",
            "continent_asia": "Asia",
            "continent_north_america": "North America",
            "continent_south_america": "South America",
            "continent_africa": "Africa",
            "continent_australia": "Australia and Oceania",
            "available": "Available",
            "coming_soon": "Coming soon",
            "select": "Select",

            "countries_in": "Countries in {0}",
            "select_country": "Select a country to see available cities and monuments",

            "cities_in": "Cities in {0}",
            "select_city": "Select a city to see available monuments",
            "show_map": "Show map",
            "country_map": "Map of {0}",
            "soon_available": "will be available soon!",

            "monuments_in": "Monuments in {0}",
            "discover_monuments": "Discover monuments in {0}",
            "monument_details": "Details",
            "show_on_map": "On map",
            "mark_visited": "Mark as visited",
            "already_visited": "✓ Monument visited!",
            "unmark_visited": "Unmark visit",
            "verify_photo": "Verify by photo",
            "description": "Description",
            "location": "Location",
            "see_on_google_maps": "See on Google Maps",

            "map_title": "Map of monuments",
            "map_subtitle": "Click a marker to see monument details",
            "close_map": "Close map",
            "available_monuments": "Available monuments:",
            "open_interactive_map": "Open full interactive map",

            "verify_title": "Monument verification: {0}",
            "verification_info": "How does verification work?",
            "verification_description": "The system analyzes the photo and compares it with monument references using an advanced AI model. A score above 70% with low similarity to other monuments means success.",
            "verification_tips": "Tips for best results:",
            "tip_1": "• Make sure the monument is clearly visible",
            "tip_2": "• Take photos in good lighting",
            "tip_3": "• Avoid obstacles blocking the monument",
            "verification_instruction": "Take or select a photo of the monument to verify your presence.",
            "select_photo": "Select photo",
            "take_photo": "Take photo",
            "processing": "Analyzing photo...",
            "force_accept": "Force accept",
            "view_profile": "View your profile",
            "added_to_profile": "Monument added to your profile!",

            "error_loading": "Error loading data",
            "try_again": "Try again",
            "refresh": "Refresh",
            "no_monuments_found": "No monuments found for this city",
            "no_data": "No data",
            "select_file": "Select a JPG, JPEG or PNG file",
            "camera_unavailable": "Camera feature will be available soon!",
            "error_processing": "Error processing file"
        },

        "de": {
            "loading": "Wird geladen...",
            "error": "Fehler",
            "success": "Erfolg",
            "warning": "Warnung",
            "info": "Information",
            "back": "Zurück",
            "cancel": "Abbrechen",
            "confirm": "Bestätigen",
            "save": "Speichern",
            "delete": "Löschen",
            "add": "Hinzufügen",
            "edit": "Bearbeiten",
            "close": "Schließen",
            "send": "Senden",
            "search": "Suchen",

            "welcome_title": "Willkommen bei Zabytkownik!",
            "welcome_subtitle": "Entdecken, besuchen und dokumentieren Sie Ihre Abenteuer",
            "register": "Registrieren",
            "login": "Anmelden",
            "about_app": "Über die App",
            "change_theme": "Thema ändern",
            "change_language": "Sprache ändern",

            "about_app_title": "Über die App",
            "about_app_content": "Zabytkownik ist eine Anwendung, die Ihnen hilft, Ihre Besuche zu Denkmälern zu entdecken, zu dokumentieren und zu teilen. Registrieren Sie sich, um Ihr Abenteuer mit der Architekturgeschichte zu beginnen!",

            "login_title": "Anmeldung",
            "username": "Benutzername",
            "password": "Passwort",
            "login_welcome": "Willkommen zurück!",
            "login_subtitle": "Melden Sie sich an, um Ihr Abenteuer mit Denkmälern fortzusetzen",
            "no_account": "Haben Sie kein Konto?",
            "register_link": "Registrieren",

            "register_title": "Registrierung",
            "confirm_password": "Passwort bestätigen",
            "register_welcome": "Treten Sie der Community bei",
            "register_subtitle": "Erstellen Sie ein Konto, um Ihre Reisen zu entdecken und zu dokumentieren",
            "have_account": "Haben Sie bereits ein Konto?",
            "login_link": "Anmelden",

            "profile": "Profil",
            "logout": "Abmelden",
            "monuments_visited": "Anzahl der besuchten Denkmäler",
            "discover_more": "Entdecken Sie mehr Denkmäler und erhöhen Sie Ihre Punktzahl!",
            "congrats": "Glückwunsch! Sie sind ein wahrer Denkmalentdecker!",
            "visited_monuments": "Besuchte Denkmäler",
            "no_monuments": "Sie haben noch keine Denkmäler besucht",
            "start_exploring": "Beginnen Sie Ihr Abenteuer, Denkmäler zu entdecken!",
            "discover": "Denkmäler entdecken",
            "show_map": "Karte der besuchten Denkmäler anzeigen",
            "logout_confirm": "Sind Sie sicher, dass Sie sich abmelden möchten?",
            "logout_success": "Sie wurden abgemeldet",

            "continents_title": "Kontinent auswählen",
            "welcome_user": "Willkommen, {0}!",
            "select_continent": "Wählen Sie einen Kontinent, den Sie erkunden möchten",
            "continent_europe": "Europa",
            "continent_asia": "Asien",
            "continent_north_america": "Nordamerika",
            "continent_south_america": "Südamerika",
            "continent_africa": "Afrika",
            "continent_australia": "Australien und Ozeanien",
            "available": "Verfügbar",
            "coming_soon": "Demnächst verfügbar",
            "select": "Auswählen",

            "countries_in": "Länder in {0}",
            "select_country": "Wählen Sie ein Land, um verfügbare Städte und Denkmäler zu sehen",

            "cities_in": "Städte in {0}",
            "select_city": "Wählen Sie eine Stadt, um verfügbare Denkmäler zu sehen",
            "show_map": "Karte anzeigen",
            "country_map": "Karte von {0}",
            "soon_available": "wird bald verfügbar sein!",

            "monuments_in": "Denkmäler in {0}",
            "discover_monuments": "Entdecken Sie Denkmäler in {0}",
            "monument_details": "Details",
            "show_on_map": "Auf der Karte",
            "mark_visited": "Als besucht markieren",
            "already_visited": "✓ Denkmal besucht!",
            "unmark_visited": "Besuch entfernen",
            "verify_photo": "Mit Foto verifizieren",
            "description": "Beschreibung",
            "location": "Standort",
            "see_on_google_maps": "Auf Google Maps ansehen",

            "map_title": "Karte der Denkmäler",
            "map_subtitle": "Klicken Sie auf einen Marker, um Denkmaldetails zu sehen",
            "close_map": "Karte schließen",
            "available_monuments": "Verfügbare Denkmäler:",
            "open_interactive_map": "Vollständige interaktive Karte öffnen",

            "verify_title": "Denkmalverifizierung: {0}",
            "verification_info": "Wie funktioniert die Verifizierung?",
            "verification_description": "Das System analysiert das Foto und vergleicht es mit Denkmalreferenzen unter Verwendung eines fortschrittlichen KI-Modells. Eine Bewertung über 70% bei geringer Ähnlichkeit zu anderen Denkmälern bedeutet Erfolg.",
            "verification_tips": "Tipps für beste Ergebnisse:",
            "tip_1": "• Stellen Sie sicher, dass das Denkmal deutlich sichtbar ist",
            "tip_2": "• Fotografieren Sie bei gutem Licht",
            "tip_3": "• Vermeiden Sie Hindernisse, die das Denkmal verdecken",
            "verification_instruction": "Machen oder wählen Sie ein Foto des Denkmals, um Ihre Anwesenheit zu verifizieren.",
            "select_photo": "Foto auswählen",
            "take_photo": "Foto aufnehmen",
            "processing": "Foto wird analysiert...",
            "force_accept": "Akzeptanz erzwingen",
            "view_profile": "Ihr Profil anzeigen",
            "added_to_profile": "Denkmal zu Ihrem Profil hinzugefügt!",

            "error_loading": "Fehler beim Laden der Daten",
            "try_again": "Erneut versuchen",
            "refresh": "Aktualisieren",
            "no_monuments_found": "Keine Denkmäler für diese Stadt gefunden",
            "no_data": "Keine Daten",
            "select_file": "Wählen Sie eine JPG-, JPEG- oder PNG-Datei",
            "camera_unavailable": "Kamerafunktion wird bald verfügbar sein!",
            "error_processing": "Fehler bei der Verarbeitung der Datei"
        }
    }

    @classmethod
    def get_current_language(cls):
        return cls._CURRENT_LANGUAGE

    @classmethod
    def set_language(cls, language_code):
        if language_code in cls.LANGUAGES:
            cls._CURRENT_LANGUAGE = language_code
            return True
        return False

    @classmethod
    def get_text(cls, key, *args):
        lang = cls._CURRENT_LANGUAGE

        if key not in cls.TRANSLATIONS[lang] and lang != "pl":
            lang = "pl"

        text = cls.TRANSLATIONS[lang].get(key, key)

        if args:
            try:
                text = text.format(*args)
            except:
                pass

        return text

    @classmethod
    def get_available_languages(cls):
        return cls.LANGUAGES

def get_text(key, *args):
    return TranslationManager.get_text(key, *args)