
library(knitr)
library(flextable)
library(ggpubr)
library(officer)
library(ggthemes)
library(RSQLite)
library(ggplot2)
library(gridExtra)

ROOT_PATH = 'C:/myap/PhD_project/src/InterpretRator'
PARAVERBAL_FILE = file.path(ROOT_PATH, 'doc', 'paraverbal_symbol.xlsx')
PARAVERBAL_ALL_FILE = file.path(ROOT_PATH, 'doc', 'paraverbal_symbol_all.xlsx')

big_border = fp_border(color="black", width = 2)
small_border = fp_border(color="black", width = 1)
std_border = fp_border(color="black", width = 1)

my_theme <- function(x, caption, width=0.9, font_size=10) {
    ft <- x %>% flextable() %>% theme_box() %>% 
        set_table_properties(width = width, layout = "autofit") %>%
        fontsize(size = font_size, part = "all") %>%
        set_caption(caption = caption) %>%
        border_remove() %>%
        hline_top(border = big_border, part = "all") %>%
        hline_bottom(border = small_border, part = "all") %>%
        hline(i = nrow(x), border = big_border, part = "body")
    return(ft)
}

adjr_theme <- function(x, caption) {
    ft <- my_theme(x, caption)
    ft <- colformat_num(ft, j = c("No", "Count"), digits = 0)
    ft <- colformat_num(ft, j = c("R.Square", "Adjusted.R.squared", "Standard.error"), digits = 3)
    ft <- align(ft, j = c("No", "Count"), align = "center", part = "body")
    
    return(ft)
}
