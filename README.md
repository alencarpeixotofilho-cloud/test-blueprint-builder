# Blueprint e Matriz Avaliativa

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) ![LaTeX](https://img.shields.io/badge/LaTeX-008080?style=flat-square&logo=latex&logoColor=white) ![Licença MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-green?style=flat-square) ![Status](https://img.shields.io/badge/status-em%20constru%C3%A7%C3%A3o-orange?style=flat-square)

> Ferramenta para planejar provas equilibradas a partir de uma matriz de referência.

## 📌 Visão geral

A partir de uma matriz de referência (áreas, competências, pesos), calcula a distribuição de itens da prova, gera o blueprint e exporta documentos prontos para a equipe de elaboração, por período ou por prova.

## ✨ Funcionalidades

- Distribuição proporcional de itens por área e competência
- Controle de níveis cognitivos e de dificuldade-alvo
- Blueprint por prova e por período
- Exportação em PDF (LaTeX) e planilha
- Verificação de aderência de uma prova pronta ao blueprint

## 🗂️ Estrutura do repositório

```text
blueprint-matriz-avaliativa/
├── src/            # cálculo da distribuição e exportação
├── templates/      # modelos LaTeX do blueprint
├── exemplos/       # matriz de referência fictícia
├── LICENSE
└── README.md
```

## 🚀 Como usar

```bash
python -m src.blueprint --matriz exemplos/matriz.yaml --itens 100 --saida blueprint.pdf
```

## 🔒 Dados e privacidade

Este repositório **não contém dados reais** de estudantes, docentes ou instituições.
Todos os exemplos usam **dados sintéticos** gerados pelo próprio projeto
(`exemplos/gerar_dados_exemplo`), com identificadores fictícios (`Estudante 001`, `Item 001`…).
Os itens de prova usados nos exemplos são inventados para fins de demonstração.

## 🛣️ Roadmap

- [ ] Formato da matriz de referência
- [ ] Algoritmo de distribuição
- [ ] Templates LaTeX
- [ ] Verificação de aderência

## 📄 Licença

Distribuído sob a licença MIT. Veja [`LICENSE`](LICENSE).
