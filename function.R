
library('sqldf')
source('./global.R')

get_root_path <- function() {
    root_path = ''
    if(Sys.info()['sysname'] == 'Windows') {
        root_path = 'C:/myap/PhD_project/src/InterpretRator'
    } else {
        root_path = '/Users/renawang/PhD_project/src/InterpretRator'
    }
    return(root_path)
}

get_db_path <- function(interpret_type) {
    db_path = ''
    if(interpret_type == 'simultaneous_interpretation') {
        db_path = file.path(get_root_path(), 'data', 'repository', 'si_repository.db')
    } else if (interpret_type == 'interpret') {
        db_path = file.path(get_root_path(), 'data', 'repository', 'in_repository.db')
    } else if (interpret_type == 'interpret_teacher') {
        db_path = file.path(get_root_path(), 'data', 'repository', 'teacher_repository.db')
    } else if (interpret_type == 'corpus') {
        db_path = file.path(get_root_path(), 'data', 'repository', 'corpus.db')
    } else {
        print(sprintf('%s is not supported, return empty', interpret_type))
    }
    return(db_path)
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

get_transquest_data <- function(interpret_type) {
    
    con <- DBI::dbConnect(RSQLite::SQLite(), get_db_path(interpret_type))
    # get transquest predict DA and HTER data
    sql = "SELECT pd_tq.subject, pd_tq.interpret_file AS interpret_file, pd_tq.sent_en_len, pd_tq.sent_zh_len, pd_tq.sent_en, pd_tq.sent_zh, pd_tq.sent_mono_da, 
            pd_tq.sent_siamese_da, pd_tq.sent_mono_hter, pd_score.lang, pd_score.service_provider, pd_score.SCORE AS score
             FROM pd_transquest_1106 pd_tq, pd_interpret_score pd_score
             WHERE pd_tq.interpret_file = pd_score.interpret_file
             ORDER BY interpret_file ASC"
    
    data = DBI::dbGetQuery(con, sql)

    DBI::dbDisconnect(con)
    
    return(data)
}

get_delivery_data <- function(interpret_type) {
    
    con <- DBI::dbConnect(RSQLite::SQLite(), get_db_path(interpret_type))
    
    if(interpret_type == 'interpret') {
        delivery <- dplyr::filter(dbReadTable(con, 'pd_lexical_min'))
    } else if(interpret_type == 'interpret_teacher') {
        # get paraverbal and lexical attributes
        sql_lexical_attrs = "SELECT paraverbal.interpret_file, NUP, NRLUP, NPLUP, 
                  source_lex_density AS LD, source_avg_sent_wc AS ASL
                  FROM pd_interpret_paraverbal paraverbal, pd_lexical lexical 
                  where paraverbal.subject LIKE '%Consec%'
                  and paraverbal.interpret_file = lexical.file_name
                  order by paraverbal.interpret_file ASC"
        
        lexical_attrs = DBI::dbGetQuery(con, sql_lexical_attrs)
        
        # get speed
        sql_speed = "SELECT interpret_file, ROUND((count(*) / (max(speak_end_time) - min(speak_start_time))), 1) AS DR
                    FROM pd_interpret_words GROUP BY interpret_file"
        
        speed = DBI::dbGetQuery(con, sql_speed)
        
        delivery = merge(lexical_attrs, speed, by="interpret_file")
    }
    
    DBI::dbDisconnect(con)
    
    return(delivery)
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

get_speech_data <- function(interpret_type, interpret_file, service_provider) {
 
    con <- DBI::dbConnect(RSQLite::SQLite(), get_db_path(interpret_type), encoding = 'UTF-8')
    # get Cross-Lingual Similarity data
    sql = sprintf("SELECT interpret_id, interpret_file, lang, speech, sentence_seq_no, word_seq_no, word, interpret_duration, speak_start_timestamp 
                    FROM pd_interpret_words
                    WHERE interpret_file = '%s' AND service_provider = '%s'
                    ORDER BY interpret_id, speak_start_timestamp ASC ", 
                  interpret_file, service_provider)
  #  print(sql)
    
    data = DBI::dbGetQuery(con, sql)
    
    DBI::dbDisconnect(con)
    
    return(data)
}

get_interpret_qe_data <- function(interpret_type) {
    
    con <- DBI::dbConnect(RSQLite::SQLite(), get_db_path(interpret_type), encoding = 'UTF-8')
    # get Cross-Lingual Similarity data
    sql = sprintf("SELECT psa.interpret_file, psa.sent_id, psa.source, psa.target, AVG(psa.assessment) AS score, pst.sent_mono_da, pst.sent_siamese_da, pst.sent_mono_hter, pss.sim
                    FROM pd_sentence_assessment psa
                    LEFT JOIN pd_sentence_tq pst
                    ON psa.interpret_file = pst.interpret_file
                    AND psa.sent_id = pst.sent_id
                    LEFT JOIN pd_sentence_similarity pss 
                    ON psa.interpret_file = pss.interpret_file
                    AND psa.sent_id = pss.sent_id
                    GROUP BY psa.interpret_file, psa.sent_id ")
    
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



