
library(knitr)
library(flextable)
library(ggpubr)
library(officer)
library(ggthemes)
library(RSQLite)
library(ggplot2)
library(gridExtra)





ROOT_PATH = ''

if(Sys.info()['sysname'] == 'Windows') {
  ROOT_PATH = 'C:/myap/PhD_project/src/InterpretRator'
} else {
  ROOT_PATH = '/Users/renawang/PhD_project/src/InterpretRator'
}

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

# mytheme <- theme(plot.title = element_text(face = "bold", size = (12)), 
#                  legend.title = element_text(colour= "steelblue", face="bold.italic"), 
#                  legend.text = element_text(face= "italic", colour="steelblue4"), 
#                  axis.title = element_text(size = (10), colour = "steelblue4"),
#                  axis.text = element_text(colour = "cornflowerblue", size = (10)),
#                  axis.text.x = element_text(colour = "cornflowerblue", size = (10)))

# big_border = fp_border(color="black", width = 2)
# small_border = fp_border(color="black", width = 1)
# 
# my_theme <- function(x, caption) {
#     
#     ft <- x %>% flextable() %>% theme_box() %>% 
#         set_table_properties(width = 0.9, layout = "autofit") %>%
#         fontsize(size = 11, part = "all") %>%
#         set_caption(caption = caption) %>%
#         border_remove() %>%
#         hline_top(border = big_border, part = "all") %>%
#         hline_bottom(border = small_border, part = "all") %>%
#         hline(i = nrow(x), border = big_border, part = "body")
#     return(ft)
# }
# 
# adjr_theme <- function(x, caption) {
#     
#     ft <- my_theme(x, caption)
#     ft <- colformat_num(ft, j = c("No", "Count"), digits = 0)
#     # ft <- colformat_num(ft, j = c("R.Square", "Adjusted.R.squared", "Mallows.Cp", "Standard.Error"), digits = 3)
#     ft <- colformat_num(ft, j = c("R.Square", "Adjusted.R.squared", "Standard.error"), digits = 3)
#     ft <- align(ft, j = c("No", "Count"), align = "center", part = "body")
#     
#     return(ft)
# }
