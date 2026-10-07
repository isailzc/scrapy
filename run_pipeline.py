import subprocess
from pathlib import Path
import pandas as pd
import typer

app = typer.Typer(help="Automatización de scraping y procesamiento de eventos de UFC")

# Definir rutas relativas con pathlib respecto a la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent
FIGHTMATRIX_DIR = BASE_DIR / "fightmatrix"
DATA_DIR = BASE_DIR / "data"

RAW_FIGHTERS = DATA_DIR / "raw_fighters.json"
RAW_MATCHUPS = DATA_DIR / "raw_matchups.json"
PROCESSED_MERGED = DATA_DIR / "latest_event.json"


def run_spiders(event_url: str):
    """Ejecuta las dos spiders de Scrapy pasándoles la URL dada."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Eliminar descargas anteriores si existen
    if RAW_FIGHTERS.exists():
        RAW_FIGHTERS.unlink()
    if RAW_MATCHUPS.exists():
        RAW_MATCHUPS.unlink()

    typer.echo("🕷️  [1/3] Extrayendo datos de peleadores...")
    subprocess.run(
        [
            "scrapy", "crawl", "fightmatrixspider",
            "-a", f"url={event_url}",
            "-o", str(RAW_FIGHTERS)
        ],
        cwd=FIGHTMATRIX_DIR,
        check=True
    )

    typer.echo("🕷️  [2/3] Extrayendo matchups del evento...")
    subprocess.run(
        [
            "scrapy", "crawl", "fightsnames",
            "-a", f"url={event_url}",
            "-o", str(RAW_MATCHUPS)
        ],
        cwd=FIGHTMATRIX_DIR,
        check=True
    )


def process_and_merge() -> pd.DataFrame:
    """Procesa y une los archivos JSON generados por Scrapy."""
    typer.echo("📊 [3/3] Transformando y uniendo datasets...")
    
    df_fighters = pd.read_json(RAW_FIGHTERS)
    df_matchups = pd.read_json(RAW_MATCHUPS)

    # Separar peleadores
    df_matchups[["fighter_1", "fighter_2"]] = df_matchups["matchup"].str.split(" vs ", expand=True)

    # Realizar merges
    df_merged = df_matchups.merge(
        df_fighters.add_suffix("_f1"),
        left_on="fighter_1",
        right_on="fighter_f1",
        how="left",
    ).merge(
        df_fighters.add_suffix("_f2"),
        left_on="fighter_2",
        right_on="fighter_f2",
        how="left",
    )

    # Guardar versión consolidada estandarizada
    df_merged.to_json(PROCESSED_MERGED, orient="records", indent=4)
    typer.echo(f"✅ Proceso completado. Datos guardados en: {PROCESSED_MERGED}")
    
    return df_merged


@app.command()
def main(
    url: str = typer.Argument(..., help="URL del evento en Fightmatrix"),
    open_notebook: bool = typer.Option(False, "--notebook", "-n", help="Abrir Jupyter Lab / Notebook al finalizar")
):
    """
    Scrapea un evento de Fightmatrix y actualiza el dataset procesado listo para el análisis.
    """
    try:
        run_spiders(url)
        process_and_merge()

        if open_notebook:
            typer.echo("🚀 Abriendo Jupyter Notebook...")
            subprocess.run(["jupyter", "lab"], cwd=BASE_DIR)

    except Exception as e:
        typer.secho(f"❌ Error durante la ejecución: {e}", fg=typer.colors.RED)


if __name__ == "__main__":
    app()