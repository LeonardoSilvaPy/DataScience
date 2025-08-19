
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def main():
    # 1) Carregar dados
    url1 = "https://raw.githubusercontent.com/alura-es-cursos/challenge1-data-science/refs/heads/main/base-de-dados-challenge-1/loja_1.csv"
    url2 = "https://raw.githubusercontent.com/alura-es-cursos/challenge1-data-science/refs/heads/main/base-de-dados-challenge-1/loja_2.csv"
    url3 = "https://raw.githubusercontent.com/alura-es-cursos/challenge1-data-science/refs/heads/main/base-de-dados-challenge-1/loja_3.csv"
    url4 = "https://raw.githubusercontent.com/alura-es-cursos/challenge1-data-science/refs/heads/main/base-de-dados-challenge-1/loja_4.csv"

    loja1 = pd.read_csv(url1)
    loja2 = pd.read_csv(url2)
    loja3 = pd.read_csv(url3)
    loja4 = pd.read_csv(url4)

    loja1["loja"] = "Loja 1"
    loja2["loja"] = "Loja 2"
    loja3["loja"] = "Loja 3"
    loja4["loja"] = "Loja 4"

    df = pd.concat([loja1, loja2, loja3, loja4], ignore_index=True)

    # 2) Métricas principais
    faturamento = df.groupby("loja")["preco"].sum().sort_values(ascending=False)
    avaliacao_media = df.groupby("loja")["avaliacao"].mean().sort_values(ascending=False)
    frete_medio = df.groupby("loja")["frete"].mean().sort_values(ascending=True)

    # 3) Score de eficiência (menor rank = melhor eficiência)
    # - Faturamento (quanto maior, melhor) => rank asc=False
    # - Avaliação média (quanto maior, melhor) => rank asc=False
    # - Frete médio (quanto menor, melhor) => rank asc=True
    # Pesos: faturamento 0.5, avaliação 0.4, frete 0.1
    # Normalizamos via rank para evitar escala diferente
    r_fat = df.groupby("loja")["preco"].sum().rank(ascending=False, method="min")
    r_ava = df.groupby("loja")["avaliacao"].mean().rank(ascending=False, method="min")
    r_fre = df.groupby("loja")["frete"].mean().rank(ascending=True, method="min")

    score = (0.5 * r_fat) + (0.4 * r_ava) + (0.1 * r_fre)
    score = score.sort_values()  # menor = melhor (mais eficiente)

    loja_mais_eficiente = score.index[0]
    loja_menos_eficiente = score.index[-1]

    # 4) Gráfico 1: Barras de Faturamento por Loja
    plt.figure(figsize=(8, 5))
    faturamento.plot(kind="bar")
    plt.title("Faturamento Total por Loja")
    plt.ylabel("Faturamento (R$)")
    plt.xlabel("Loja")
    plt.xticks(rotation=0)
    fig1 = plt.gcf()

    # 5) Gráfico 2: Pizza - Categorias mais vendidas da loja menos eficiente
    categorias = df[df["loja"] == loja_menos_eficiente]["categoria"].value_counts()
    plt.figure(figsize=(6, 6))
    categorias.plot(kind="pie", autopct="%1.1f%%", startangle=90)
    plt.title(f"Categorias mais vendidas - {loja_menos_eficiente}")
    plt.ylabel("")
    fig2 = plt.gcf()

    # 6) Gráfico 3: Dispersão Preço x Avaliação (todas as lojas)
    plt.figure(figsize=(8, 5))
    plt.scatter(df["preco"], df["avaliacao"], alpha=0.6)
    plt.title("Preço x Avaliação dos Produtos")
    plt.xlabel("Preço (R$)")
    plt.ylabel("Avaliação")
    fig3 = plt.gcf()

    # 7) Gera PDF com os gráficos e a recomendação final
    with PdfPages("relatorio_alura_store.pdf") as pdf:
        pdf.savefig(fig1, bbox_inches="tight")
        pdf.savefig(fig2, bbox_inches="tight")
        pdf.savefig(fig3, bbox_inches="tight")

        # Página final com texto (conclusões)
        resumo = []
        resumo.append("# Relatório de Análise - Alura Store")
        resumo.append("")
        resumo.append("## Métricas por Loja")
        resumo.append("Faturamento total (R$):")
        for loja, valor in df.groupby("loja")["preco"].sum().sort_values(ascending=False).items():
            resumo.append(f" - {loja}: R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        resumo.append("")
        resumo.append("Avaliação média:")
        for loja, valor in df.groupby("loja")["avaliacao"].mean().sort_values(ascending=False).items():
            resumo.append(f" - {loja}: {valor:.2f}")
        resumo.append("")
        resumo.append("Frete médio (R$):")
        for loja, valor in df.groupby("loja")["frete"].mean().sort_values(ascending=True).items():
            resumo.append(f" - {loja}: R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        resumo.append("")
        resumo.append("## Eficiência (menor score = mais eficiente)")
        for loja, valor in score.items():
            resumo.append(f" - {loja}: {valor:.2f}")
        resumo.append("")
        resumo.append("## Recomendação")
        resumo.append(f"Com base no score de eficiência calculado (considerando faturamento, avaliação média e frete), a loja menos eficiente é **{loja_menos_eficiente}**.")
        resumo.append(f"Recomenda-se vender a **{loja_menos_eficiente}**, pois apresenta pior desempenho relativo ao portfólio, enquanto a mais eficiente é **{loja_mais_eficiente}**.")
        resumo_texto = "\n".join(resumo)

        # Criar página de texto
        plt.figure(figsize=(8.27, 11.69))  # Aproximadamente A4
        plt.axis("off")
        plt.text(0.02, 0.98, resumo_texto, va="top", ha="left", wrap=True, fontsize=11)
        pdf.savefig(bbox_inches="tight")
        plt.close("all")

    # 8) Também imprime no console a recomendação principal
    print("="*60)
    print("RECOMENDAÇÃO FINAL")
    print(f"Vender: {loja_menos_eficiente}")
    print(f"Mais eficiente: {loja_mais_eficiente}")
    print("="*60)

if __name__ == "__main__":
    main()
