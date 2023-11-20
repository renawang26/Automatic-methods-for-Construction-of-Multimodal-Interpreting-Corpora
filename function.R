
library('sqldf')
source('./global.R')

get_root_path <- function() {
    return('C:/myap/PhD_project/src/InterpretRator')
}

get_db_path <- function() {
    return(file.path(get_root_path(), 'data', 'repository', 'in_repository.db'))
}

get_edit_words_similarity <- function(interpret_type) {
    
    con <- DBI::dbConnect(RSQLite::SQLite(), get_db_path(interpret_type))
    
    sql = sprintf("SELECT file_name AS interpret_file, sent_id, word_id, b.word, b.word_edit, CAST(word_upd AS NUMERIC) AS is_upd_num, 
                    CAST(word_condifence AS NUMERIC) AS confidence, CAST(word_similarity AS NUMERIC) AS similarity, a.SCORE  
                             FROM pd_interpret_words a, pd_phd_file_word_confidence_similarity b
                             WHERE a.interpret_file = b.file_name AND a.sentence_seq_no = b.sent_id AND a.word_seq_no = b.word_id AND a.SCORE > 0")
    
    words = DBI::dbGetQuery(con, sql)
    DBI::dbDisconnect(con)
    
    return(words)
}

