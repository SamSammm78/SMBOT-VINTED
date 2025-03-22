import os
import discord
import asyncio
import json
from discord.ext import commands
from discord.ui import View, Button
from dotenv import load_dotenv
from scraper import scrape_vinted  # 🔥 Importation du scraper

# Chargement des fichiers JSON
CONFIG_FILE = "config.json"
LINKS_FILE = "links.json"

# Charger la configuration
with open(CONFIG_FILE, "r", encoding="utf-8") as file:
    config = json.load(file)

MAX_ARTICLES = config["vintedSettings"]["maxItemsPerSearch"]
INTERVAL = config["vintedSettings"]["searchIntervalSecondes"]
PREFIX = config["prefix"]

# Vérifier si links.json existe, sinon le créer
if not os.path.exists(LINKS_FILE):
    with open(LINKS_FILE, "w", encoding="utf-8") as file:
        json.dump({"searches": []}, file, indent=4, ensure_ascii=False)

# Charger les variables d'environnement
load_dotenv()
TOKEN = str(os.getenv("TOKEN_BOT_DISCORD"))

# Initialisation du bot
intents = discord.Intents.all()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="$", intents=intents)

# Stockage des anciens articles
old_articles = set()

async def check_new_items():
    """Scrape Vinted en arrière-plan toutes les minutes sans bloquer le bot."""
    global old_articles

    await bot.wait_until_ready()  # S'assurer que le bot est bien connecté

    while not bot.is_closed():
        try:
            # Charger les liens depuis links.json
            with open(LINKS_FILE, "r", encoding="utf-8") as file:
                links_data = json.load(file)

            for item in links_data["searches"]:
                channel = bot.get_channel(item["channel_id"])
                if not channel:
                    print(f"⚠️ Impossible de trouver le canal {item['channel_id']}")
                    continue

                articles = scrape_vinted(item["url"])
                new_articles = [a for a in articles if a["url"] not in old_articles]

                if new_articles:
                    for article in new_articles[:MAX_ARTICLES]:  # Max 5 annonces par tour
                        embed = discord.Embed(
                            title=item["name"],
                            description=f"💰 Prix : {article['price']}",
                            color=discord.Color.green()
                        )
                        embed.set_thumbnail(url=article["image_url"])

                        bouton = Button(label="Voir l'annonce", url=article["url"])
                        view = View()
                        view.add_item(bouton)

                        await channel.send(embed=embed, view=view)
                        old_articles.add(article["url"])  # Stocker pour éviter les doublons

                await asyncio.sleep(5)  # Éviter de spammer le site

        except Exception as e:
            print(f"Erreur dans le scraping : {e}")

        await asyncio.sleep(INTERVAL)  # Attendre 1 minute avant de recommencer

@bot.event
async def on_ready():
    print(f"{bot.user} est en ligne ! ✅")
    asyncio.create_task(check_new_items())  # Lancer le scraping en arrière-plan

@bot.command()
async def add_link(ctx, nom: str, lien: str, channel: discord.TextChannel):
    """Ajoute un lien Vinted dans links.json"""

    # Charger links.json
    try:
        with open(LINKS_FILE, "r", encoding="utf-8") as file:
            links_data = json.load(file)
    except FileNotFoundError:
        links_data = {"searches": []}

    # Vérifier si le lien est déjà présent
    for search in links_data["searches"]:
        if search["url"] == lien:
            await ctx.send("❌ Ce lien est déjà enregistré.")
            return

    # Ajouter la nouvelle recherche
    nouvelle_recherche = {
        "name": nom,
        "url": lien,
        "channel_id": channel.id,
        "enabled": True
    }
    links_data["searches"].append(nouvelle_recherche)

    # Sauvegarder dans links.json
    with open(LINKS_FILE, "w", encoding="utf-8") as file:
        json.dump(links_data, file, indent=4, ensure_ascii=False)

    await ctx.send(f"✅ Le lien **{nom}** a été ajouté et les annonces seront envoyées dans {channel.mention} !")

@bot.command()
async def ping(ctx):
    """Commande pour tester la latence du bot"""
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

@bot.command()
async def stop(ctx):
    """Arrête le bot"""
    if ctx.author.guild_permissions.administrator:
        await ctx.send("Arrêt du bot...")
        await bot.close()
    else:
        await ctx.send("❌ Tu n'as pas la permission d'exécuter cette commande.")

@bot.command()
async def list_links(ctx):
    """Affiche la liste des liens enregistrés"""

    try:
        with open("links.json", "r", encoding="utf-8") as file:
            links_data = json.load(file)
    except FileNotFoundError:
        await ctx.send("❌ Aucun lien enregistré.")
        return

    if not links_data["searches"]:
        await ctx.send("❌ Aucun lien enregistré.")
        return

    embed = discord.Embed(
        title="📌 Liste des liens enregistrés",
        color=discord.Color.blue()
    )

    for link in links_data["searches"]:
        channel_mention = f"<#{link['channel_id']}>"  # Mentionne le channel
        embed.add_field(
            name=link["name"], 
            value=f"🔗 [Lien Vinted]({link['url']})\n📢 Canal : {channel_mention}",
            inline=False
        )

    await ctx.send(embed=embed)
    

bot.run(TOKEN)
