import pywikibot

site = pywikibot.Site("fr", "vikidia")
category_name = "Jeu vidéo"
portail_normalisé = "Jeu vidéo"

# Variantes acceptées du nom du portail
variante_portails = {
    "jeu vidéo",
    "jeux vidéo",
    "jeux vidéos",  # faute fréquente
    "Jeu Vidéo",
    "Jeux Vidéo",
    "Jeux Vidéos",
    "Jeux vidéo",   # oublié précédemment
}

def normaliser_portail(nom):
    """Normalise une chaîne de portail pour comparaison."""
    return nom.strip().lower()

def get_portails_existants(page):
    """Retourne tous les portails présents dans les modèles {{Portail}}."""
    portails = []
    for template, params in page.templatesWithParams():
        if template.title(with_ns=False).lower() == "portail":
            portails.extend(params)
    return [normaliser_portail(p) for p in portails]

def mettre_à_jour_portail(text):
    """Ajoute ou fusionne le portail dans un modèle {{Portail|...}} existant."""
    lines = text.splitlines()
    modifié = False
    for i, line in enumerate(lines):
        if "{{Portail" in line.lower():
            début = line.find("{{")
            fin = line.find("}}", début)
            if fin == -1:
                continue

            contenu = line[début + 2:fin]
            morceaux = contenu.split("|")
            nom_modele = morceaux[0].strip()
            portails = [p.strip() for p in morceaux[1:]]
            portails_norm = [normaliser_portail(p) for p in portails]

            # Ajouter si pas déjà présent (en tenant compte des variantes)
            if not any(p in variante_portails for p in portails_norm):
                portails.append(portail_normalisé)
                nouvelle_ligne = f"{{{{{nom_modele}|{'|'.join(portails)}}}}}"
                lines[i] = nouvelle_ligne
                modifié = True
            return "\n".join(lines), modifié

    # Aucun modèle {{Portail}} trouvé, on en ajoute un en bas
    lines.append(f"\n{{{{Portail|{portail_normalisé}}}}}")
    modifié = True
    return "\n".join(lines), modifié


def process_pages():
    cat = pywikibot.Category(site, f"Catégorie:{category_name}")
    for page in cat.articles(namespaces=0):
        print(f"→ Traitement de : {page.title()}")
        try:
            existants = get_portails_existants(page)
            if any(p in variante_portails for p in existants):
                print("   [=] Portail déjà présent (variante détectée).")
                continue

            old_text = page.get()
            new_text, modifié = mettre_à_jour_portail(old_text)

            if modifié and new_text != old_text:
                page.put(new_text, summary=f"Ajout ou mise à jour du modèle {{Portail|{portail_normalisé}}}")
                print("   [+] Portail mis à jour.")
            else:
                print("   [=] Aucun changement.")
        except Exception as e:
            print(f"   [!] Erreur : {e}")

process_pages()
