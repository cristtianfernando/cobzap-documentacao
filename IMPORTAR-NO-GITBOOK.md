# Como publicar este conteúdo no GitBook

## Opção recomendada: Git Sync

1. Crie um repositório vazio no GitHub ou GitLab.
2. Extraia este pacote dentro do repositório.
3. Revise `README.md`, `SUMMARY.md` e os endereços da marca.
4. Faça commit e push.
5. No espaço do GitBook, selecione **Set up Git Sync**.
6. Escolha o repositório e a branch.
7. Na sincronização inicial, escolha **GitHub/GitLab → GitBook**.
8. Revise a prévia antes de publicar.

## Importação por ZIP

O GitBook também permite importar Markdown por ZIP, mas a importação direta possui limites de páginas e arquivos. Para esta estrutura, prefira Git Sync.

## Para adaptar um export autorizado existente

Faça primeiro uma cópia de segurança e execute:

```bash
python tools/migrar_marca.py /caminho/do/export
python tools/migrar_marca.py /caminho/do/export --apply
```

Para substituições adicionais:

```bash
python tools/migrar_marca.py /caminho/do/export   --config config/replacements.example.json   --apply
```

## Revisão obrigatória

A troca de marca não valida automaticamente:

- URLs externas;
- screenshots e vídeos;
- logotipos;
- nomes de menus;
- planos e preços;
- requisitos técnicos;
- endpoints;
- políticas jurídicas;
- recursos que não existam no Cobzap.

Use `RELATORIO_REVISAO_MARCA.txt` para localizar referências remanescentes.
