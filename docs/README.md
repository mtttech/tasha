# TASHA

**Tasha** is a tool for creating player characters for the 5th edition *Dungeons & Dragons (2024)* tabletop game.

### Supported rulebooks

Below is a list of rulebooks incorporated into the program (more may be added as they become available).

  * [Player's Handbook 2024](https://www.amazon.com/Dungeons-Dragons-Players-Handbook-Rulebook/dp/0786969512/ref=sr_1_1?crid=Q5CVDF9LEKCR&dib=eyJ2IjoiMSJ9.KggBZNS4k50B6gIGZykwyAllHlDPYc0OKbcSPRUnOeaf7xarl1Qh75B-svm690jDc5Ubb8NE7-FQlF93zPqJ4nzpY9hKrLipiAh3VdIXeklwDRgL2xhQ4qlb6L5frqXVCqZ5F1owxNa8HJ0u-NuittVd-wUBE2oeEdJ71qed1yNp4NM-Xmo6BZeInTeROhQtepObqQHkIYTsFvWXlIEA_iVEtS8JKbZkLz0AxGnJY9U.zsuk-fEv2n0ZfuKE8fzhKVaVLpChNEwjNZm2S8lZZIk&dib_tag=se&keywords=players%2Bhandbook%2B5e%2B2024&qid=1727028562&sprefix=players%2Caps%2C149&sr=8-1&th=1)

## Usage

Get the current version of tasha.

```
go run tasha version
```

Create a new character with the following command.

```
go run tasha new <CHARACTER_NAME>
```

# TODO List

* Basic multiclass selection implemented but doesn't check for multiclass ability score requirements. Planning to add this functionality next.