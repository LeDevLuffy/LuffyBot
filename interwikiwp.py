import pywikibot
import os
import threading
import ping
import stopifpdd

FICHIER_PAGES_TRAITEES = "pages_traiteesinterwiki.txt"

def charger_pages_traitees():
    """Charge la liste des pages déjà traitées à partir du fichier."""
    if os.path.exists(FICHIER_PAGES_TRAITEES):
        with open(FICHIER_PAGES_TRAITEES, "r", encoding="utf-8") as f:
            return set(f.read().splitlines())
    return set()

def enregistrer_page_traitee(page_title):
    """Ajoute une page traitée au fichier."""
    with open(FICHIER_PAGES_TRAITEES, "a", encoding="utf-8") as f:
        f.write(page_title + "\n")

def ajouter_liens_wikipedia():
    site_vikidia = pywikibot.Site()  # Vikidia
    site_wikipedia = pywikibot.Site("fr", "wikipedia")  # Wikipédia FR
    pages_traitees = charger_pages_traitees()

    for page in site_vikidia.allpages(namespace=0):
        try:
            # Vérifier si la page est une redirection
            if page.isRedirectPage():
                print(f"Skip: {page.title()} est une redirection.")
                continue

            # Vérifier si la page a déjà été traitée
            if page.title() in pages_traitees:
                print(f"Skip: {page.title()} a déjà été traitée.")
                continue

            # Vérifier si la page contient déjà un lien Wikipédia
            if "[[wp:" in page.text.lower():
                print(f"Skip: {page.title()} contient déjà un lien vers Wikipédia.")
                continue

            # Vérifier si la page existe sur Wikipédia
            page_wikipedia = pywikibot.Page(site_wikipedia, page.title())
            if page_wikipedia.exists():
                # Ajouter le lien interwiki
                lien_wp = f"[[wp:{page.title()}]]"
                page.text += f"\n\n{lien_wp}"
                page.save(f"Interwiki(Wikipédia) : {lien_wp}")
                print(f"Lien ajouté sur '{page.title()}'")

                # Enregistrer la page traitée
                enregistrer_page_traitee(page.title())
            else:
                print(f"Pas de correspondance sur Wikipédia pour '{page.title()}'.")

        except Exception as e:
            print(f"Erreur sur '{page.title()}': {e}")

# Lancer les threads pour le ping et l'arrêt sur modification de la PDD
threading.Thread(target=ping.envoyer_ping, daemon=True).start()
threading.Thread(target=stopifpdd.stop_pdd, daemon=True).start()

# Exécution du script
ajouter_liens_wikipedia()
