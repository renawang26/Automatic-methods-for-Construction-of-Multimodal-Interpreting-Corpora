
library('sqldf')
source('./global.R')

get_root_path <- function() {
    return('C:/myap/PhD_project/src/InterpretRator')
}

get_db_path <- function() {
    return(file.path(get_root_path(), 'data', 'repository', 'in_repository.db'))
}

get_edit_words <- function(lang, service_provider, has_score, interpret_type) {
    
    con <- DBI::dbConnect(RSQLite::SQLite(), get_db_path(interpret_type))
    
    sql = sprintf("SELECT interpret_file, IIF(word==edit_word, 0, 1) AS is_upd_num, confidence, SCORE, lang, service_provider
                  FROM pd_interpret_words WHERE lang = '%s' AND service_provider = '%s' ", 
                  lang, service_provider)
    
    if(has_score) {
        sql = paste(sql, " AND SCORE > 0")
    }
    
    words = DBI::dbGetQuery(con, sql)
    DBI::dbDisconnect(con)
    
    return(words)
}

get_edit_words_similarity <- function(has_score, interpret_type) {
    
    con <- DBI::dbConnect(RSQLite::SQLite(), get_db_path(interpret_type))
    
    sql = sprintf("SELECT file_name AS interpret_file, sent_id, word_id, b.word, b.word_edit, CAST(word_upd AS NUMERIC) AS is_upd_num, 
                    CAST(word_condifence AS NUMERIC) AS confidence, CAST(word_similarity AS NUMERIC) AS similarity, a.SCORE  
                             FROM pd_interpret_words a, pd_phd_file_word_confidence_similarity b
                             WHERE a.interpret_file = b.file_name AND a.sentence_seq_no = b.sent_id AND a.word_seq_no = b.word_id ")
    
    if(has_score) {
        sql = paste(sql, " AND a.SCORE > 0")
    }
    
    words = DBI::dbGetQuery(con, sql)
    DBI::dbDisconnect(con)
    
    return(words)
}

get_pvalue <- function(model_sum) {
    return(format.pval(pf(model_sum$fstatistic[1L], model_sum$fstatistic[2L], model_sum$fstatistic[3L], lower.tail = FALSE)))
}

get_similarity_data <- function(interpret_type) {
    
    con <- DBI::dbConnect(RSQLite::SQLite(), get_db_path(interpret_type))
    # get Cross-Lingual Similarity data
    sql = "SELECT interpret_file, en_idx, zh_idx, en, zh, avg(sim) AS sim, SCORE AS score, lang, service_provider, speech, subject
          FROM cross_lingual_similarity_all
          WHERE SCORE > 0 AND (zh_idx-en_idx) <= 0 AND (zh_idx-en_idx) >= 0
          GROUP BY interpret_file
          ORDER BY interpret_file ASC"
    
    data = DBI::dbGetQuery(con, sql)
    
    DBI::dbDisconnect(con)
    
    return(data)
}

get_similarity_ex_data <- function(interpret_type) {
    
    con <- DBI::dbConnect(RSQLite::SQLite(), get_db_path(interpret_type))
    # get Cross-Lingual Similarity data
    sql = "SELECT * FROM cross_lingual_similarity_ex ORDER BY interpret_file ASC"
    
    data = DBI::dbGetQuery(con, sql)
    
    DBI::dbDisconnect(con)
    
    return(data)
}

get_interpret_files <- function(interpret_type) {
    
    con <- DBI::dbConnect(RSQLite::SQLite(), get_db_path(interpret_type))
    # get Cross-Lingual Similarity data
    sql = "SELECT interpret_file 
                    FROM interpret
                    WHERE service_provider = 'ibm'
                    ORDER BY id ASC "
    
    data = DBI::dbGetQuery(con, sql)
    
    DBI::dbDisconnect(con)
    
    return(data)
}

flattenCorrMatrix <- function(cormat, pmat) {
    ut <- upper.tri(cormat)
    data.frame(
        row = rownames(cormat)[row(cormat)[ut]],
        column = rownames(cormat)[col(cormat)[ut]],
        cor  =(cormat)[ut],
        p = pmat[ut]
    )
}



