##########################################################
############## Picturing Stories Evaluation ##############
##########################################################

library(jsonlite)
library(dplyr)

#######################################
#### Load and Clean JSON OUTPUTS ######
#######################################

# Input Model Outputs T0-T4
df <- stream_in(file("T0-T4_All_Models_Output.jsonl")) %>%
  mutate(
    characters = sapply(characters, paste, collapse = ";"),
    objects    = sapply(objects,     paste, collapse = ";")
  )

# Input model outputs T5
df2 <- stream_in(file("T5_All_Models_Output.jsonl")) %>%
  mutate(actions = sapply(actions, paste, collapse = ";"))

# Normalize filename
df <- df %>%
  mutate(image = sub("^.*?_(?=[^_]*_[^_]*$)", "", image, perl = TRUE))

df2 <- df2 %>%
  mutate(image = sub("^.*?_(?=[^_]*_[^_]*$)", "", image, perl = TRUE))

length(which(!df2$image %in% df$image))

df2$image[which(!df2$image %in% df$image)][1]

meta<-list.files("Illustrations_IA_Sample")

meta2 <- sub("^.*?_(?=[^_]*_[^_]*$)", "", meta, perl = TRUE)
length(which(df2$image %in% meta2))
length(which(df$image %in% meta2))

write.csv(df, file="DATA_Evaluation_T0_T4.csv", row.names = F)
write.csv(df2, file="DATA_Evaluation_T5.csv", row.names = F)

######## Combine with human answers ########

# For T0-T4
a<-read.csv("DATA_Illustration_IA_Annotations_Consensus_All.csv")
a<-a[which(a$filename %in% df$image),]
df.h <- df %>%
  left_join(a %>% select(filename, T0, T1, T2, T3, T4,captions),
            by = c("image" = "filename"))

write.csv(df.h, file="DATA_Illustration_IA_Evaluation_T0_T4.csv", row.names = F)

# For T5
a<-read.csv("DATA_Illustration_IA_Annotations_Consensus_All.csv")
a<-a[which(a$filename %in% df2$image),]
df.h2 <- df2 %>%
  left_join(a %>% select(filename, T5),
            by = c("image" = "filename"))

write.csv(df.h2, file="DATA_Illustration_IA_Evaluation_T5.csv", row.names = F)

# Total illustrations
# add caption data
cap<-read.csv("DATA_Illustration_IA_Caption_Validation_Clean4.csv")
v<-append(df.h$image, df.h2$image)
length(unique(v))
v2<-append(gsub(".jpg", "", v), cap$pageID)
length(unique(v2))

#######################################
####### Analyze Setting Errors ########
#######################################

df<-read.csv("DATA_Illustration_IA_Evaluation_T0_T4.csv")
# remove NA
df<-df[!is.na(df$T0),]

# Remove multiple answer rows
df<-df[-grep(",", df$T2),]

#identify errors
err<-df[which(df$scene_setting != df$T2),]

#for best model
err<-err[err$model == "gemini-2.5-flash",]
err<-err[err$shot_type == "zeroshot",]
length(unique(err$image))
table(err$scene_setting)

t<-err[err$T2 == "Indoors",]

t2<-df[df$T2 == "Indoors" | df$T2 == "Outdoors",]
t2<-t2[t2$scene_setting == "Indoors" | t2$scene_setting == "Outdoors",]
nrow(t2[t2$scene_setting == t2$T2,])/nrow(t2)

# Confusion matrix
m<-df[df$model == "gemini-2.5-flash" & df$shot_type == "zeroshot",]
m <- m %>%
  filter(m$scene_setting != "Ambiguous")
table(predicted = m$scene_setting, actual = m$T2)


##########################################
####### Analyze Character Errors #########
##########################################

df<-read.csv("DATA_Illustration_IA_Evaluation_T0_T4.csv")
# remove NA
df<-df[which(df$T0 == "Yes"),]
df<-df[which(df$illustration_present == "Yes"),]

#Subset by model
df<-df[which(df$model == "gemini-2.5-flash"),]
df<-df[which(df$shot_type == "zeroshot"),]

##### Test 1: Character Frequency #####

df$n_model <- sapply(strsplit(df$characters, "[;,]"), function(x) {
  if (all(is.na(x))) return(NA)
  x <- str_trim(x)
  if (all(x == "None")) return(0)
  sum(x != "" & x != "None")
})

df$n_human <- sapply(strsplit(df$T1, ","), function(x) {
  if (all(is.na(x))) return(NA)
  x <- str_trim(x)
  if (all(x == "None")) return(0)
  sum(x != "" & x != "None")
})

summarize_counts <- function(x, label) {
  cat(label, "\n")
  cat("  Mean:  ", round(mean(x, na.rm = TRUE), 2), "\n")
  cat("  Median:", median(x, na.rm = TRUE), "\n")
  cat("  SD:    ", round(sd(x, na.rm = TRUE), 2), "\n\n")
}

summarize_counts(df$n_model, "Model")
summarize_counts(df$n_human, "Human (T1)")

library(rstatix)
wilcox.test(df$n_model, df$n_human, paired = TRUE)
df_complete <- df %>% filter(!is.na(n_model) & !is.na(n_human))

df_long_paired <- data.frame(
  n = c(df_complete$n_model, df_complete$n_human),
  source = rep(c("Model", "Human"), each = nrow(df_complete))
)

wilcox_effsize(df_long_paired, n ~ source, paired = TRUE)

library(ggplot2)
library(tidyr)

# Reshape to long format
df_long <- data.frame(
  n = c(df$n_model, df$n_human),
  source = rep(c("Model", "Human"), each = nrow(df))
) %>%
  filter(!is.na(n))

# Plot
ggplot(df_long, aes(x = n, fill = source)) +
  geom_histogram(binwidth = 1, position = "identity", alpha = 0.5) +
  scale_fill_manual(values = c("Model" = "steelblue", "Human" = "coral")) +
  labs(
    x = "Number of Characters",
    y = "Count",
    fill = "Source",
    title = "Distribution of Character Counts: Model vs. Human"
  ) +
  theme_minimal()

##### Test 2: Frequency by Type #####
library(dplyr)
library(tidyr)
library(stringr)

# Model categories (semicolon-separated)
model_cats <- df %>%
  separate_rows(characters, sep = "[;,]") %>%
  mutate(characters = str_trim(characters)) %>%
  filter(characters != "") %>%
  count(characters) %>%
  rename(category = characters, n_model = n)

model_cats <- model_cats %>%
  mutate(category = case_when(
    category == "Animate Object" ~ "Animate Object (e.g. a teddy bear or spoon who talks)",
    TRUE ~ category
  ))

# Human categories (comma-separated)
human_cats <- df %>%
  separate_rows(T1, sep = ",") %>%     # <-- comma here
  mutate(T1 = str_trim(T1)) %>%
  filter(T1 != "") %>%
  count(T1) %>%
  rename(category = T1, n_human = n)

cats <- full_join(model_cats, human_cats, by = "category") %>%
  replace_na(list(n_model = 0, n_human = 0)) %>%
  mutate(
    prop_model = n_model / sum(n_model),
    prop_human = n_human / sum(n_human),
    diff = prop_model - prop_human
  ) %>%
  arrange(desc(diff))

cats <- cats %>%
  mutate(
    fisher_p = mapply(function(nm, nh) {
      m <- matrix(c(nm, sum(n_model) - nm, nh, sum(n_human) - nh), nrow = 2)
      fisher.test(m)$p.value
    }, n_model, n_human),
    odds_ratio = mapply(function(nm, nh) {
      m <- matrix(c(nm, sum(n_model) - nm, nh, sum(n_human) - nh), nrow = 2)
      fisher.test(m)$estimate
    }, n_model, n_human)
  )

##########################################
####### Analyze Object Errors ############
##########################################

##### Test 1: Object Frequency #####
df$n_model_obj <- sapply(strsplit(df$objects, "[;,]"), function(x) {
  if (all(is.na(x))) return(NA)
  x <- str_trim(x)
  if (all(x == "None")) return(0)
  sum(x != "" & x != "None")
})
df$n_human_obj <- sapply(strsplit(str_remove_all(df$T3, "\\s*\\([^)]*\\)"), ","), function(x) {
  if (all(is.na(x))) return(NA)
  x <- str_trim(x)
  if (all(x == "None")) return(0)
  sum(x != "" & x != "None")
})

summarize_counts(df$n_model_obj, "Model (objects)")
summarize_counts(df$n_human_obj, "Human (T3)")

wilcox.test(df$n_model_obj, df$n_human_obj, paired = TRUE)

df_complete_obj <- df %>% filter(!is.na(n_model_obj) & !is.na(n_human_obj))
df_long_paired_obj <- data.frame(
  n = c(df_complete_obj$n_model_obj, df_complete_obj$n_human_obj),
  source = rep(c("Model", "Human"), each = nrow(df_complete_obj))
)
wilcox_effsize(df_long_paired_obj, n ~ source, paired = TRUE)

df_long_obj <- data.frame(
  n = c(df$n_model_obj, df$n_human_obj),
  source = rep(c("Model", "Human"), each = nrow(df))
) %>%
  filter(!is.na(n))
ggplot(df_long_obj, aes(x = n, fill = source)) +
  geom_histogram(binwidth = 1, position = "identity", alpha = 0.5) +
  scale_fill_manual(values = c("Model" = "steelblue", "Human" = "coral")) +
  labs(
    x = "Number of Objects",
    y = "Count",
    fill = "Source",
    title = "Distribution of Object Counts: Model vs. Human"
  ) +
  theme_minimal()

##### Test 2: Frequency by Type #####
model_obj_cats <- df %>%
  separate_rows(objects, sep = "[;,]") %>%
  mutate(objects = str_trim(objects)) %>%
  filter(objects != "") %>%
  count(objects) %>%
  rename(category = objects, n_model = n)

human_obj_cats <- df %>%
  mutate(T3 = str_remove_all(T3, "\\s*\\([^)]*\\)")) %>%  # strip parens FIRST
  separate_rows(T3, sep = ",") %>%
  mutate(T3 = str_trim(T3)) %>%
  filter(!is.na(T3), T3 != "") %>%
  count(T3) %>%
  rename(category = T3, n_human = n)

obj_cats <- full_join(model_obj_cats, human_obj_cats, by = "category") %>%
  replace_na(list(n_model = 0, n_human = 0)) %>%
  mutate(
    prop_model = n_model / sum(n_model),
    prop_human = n_human / sum(n_human),
    diff = prop_model - prop_human
  ) %>%
  arrange(desc(diff))
obj_cats <- obj_cats %>%
  mutate(
    fisher_p = mapply(function(nm, nh) {
      m <- matrix(c(nm, sum(n_model) - nm, nh, sum(n_human) - nh), nrow = 2)
      fisher.test(m)$p.value
    }, n_model, n_human),
    odds_ratio = mapply(function(nm, nh) {
      m <- matrix(c(nm, sum(n_model) - nm, nh, sum(n_human) - nh), nrow = 2)
      fisher.test(m)$estimate
    }, n_model, n_human)
  )

household_mismatch <- df %>%
  filter(
    str_detect(objects, "Household items and tools"),
    !str_detect(T3, "Household") | is.na(T3)
  )

boy_mismatch <- df %>%
  filter(
    str_detect(characters, "Boy"),
    !str_detect(T1, "Boy") | is.na(T1)
  )

###########################################
####### Analyze Emotion Errors ############
###########################################
df <- df %>%
  mutate(
    # extract all digits from T4 and average them
    T4_numeric = sapply(str_extract_all(T4, "\\d"), function(x) {
      if (length(x) == 0 || all(is.na(x))) return(NA)
      mean(as.numeric(x))
    }),
    # model is already numeric
    emotional_intensity = as.numeric(emotional_intensity),
    # distance
    intensity_distance = emotional_intensity - T4_numeric
  )


###########################################
####### Analyze Action Errors #############
###########################################

df.act<-read.csv("DATA_Illustration_IA_Evaluation_T5.csv")

#Subset by model
df.act<-df.act[which(df.act$model == "gemini-2.5-flash"),]
df.act<-df.act[which(df.act$shot_type == "zeroshot"),]

df.act <- df.act %>%
  mutate(
    T5_actions = mapply(function(entity, t5) {
      if (is.na(t5) | is.na(entity)) return(NA)
      # find the block matching the entity
      pattern <- paste0(entity, "\\[n=\\d+\\]\\{([^}]*)\\}")
      m <- str_match(t5, pattern)
      if (is.na(m[1])) return(NA)
      m[2]  # return just the actions inside {}
    }, entity, T5)
  )

df.act <- df.act %>%
  mutate(
    n_model_act = sapply(strsplit(actions, ";"), function(x) {
      if (all(is.na(x))) return(NA)
      sum(str_trim(x) != "")
    }),
    n_human_act = sapply(strsplit(T5_actions, ";"), function(x) {
      if (all(is.na(x))) return(NA)
      sum(str_trim(x) != "")
    })
  )

summarize_counts(df.act$n_model_act, "Model (actions)")
summarize_counts(df.act$n_human_act, "Human (T5)")

df_complete_act <- df.act %>% filter(!is.na(n_model_act) & !is.na(n_human_act))
df_long_paired_act <- data.frame(
  n = c(df_complete_act$n_model_act, df_complete_act$n_human_act),
  source = rep(c("Model", "Human"), each = nrow(df_complete_act))
)
wilcox_effsize(df_long_paired_act, n ~ source, paired = TRUE)

model_act_cats <- df.act %>%
  separate_rows(actions, sep = ";") %>%
  mutate(actions = str_trim(actions)) %>%
  filter(!is.na(actions), actions != "") %>%
  count(actions) %>%
  rename(category = actions, n_model = n)

human_act_cats <- df.act %>%
  separate_rows(T5_actions, sep = ";") %>%
  mutate(T5_actions = str_trim(T5_actions)) %>%
  filter(!is.na(T5_actions), T5_actions != "") %>%
  count(T5_actions) %>%
  rename(category = T5_actions, n_human = n)

act_cats <- full_join(model_act_cats, human_act_cats, by = "category") %>%
  replace_na(list(n_model = 0, n_human = 0)) %>%
  mutate(
    prop_model = n_model / sum(n_model),
    prop_human = n_human / sum(n_human),
    diff = prop_model - prop_human
  ) %>%
  arrange(desc(diff))

act_cats <- act_cats %>%
  mutate(
    fisher_p = mapply(function(nm, nh) {
      m <- matrix(c(nm, sum(n_model) - nm, nh, sum(n_human) - nh), nrow = 2)
      fisher.test(m)$p.value
    }, n_model, n_human),
    odds_ratio = mapply(function(nm, nh) {
      m <- matrix(c(nm, sum(n_model) - nm, nh, sum(n_human) - nh), nrow = 2)
      fisher.test(m)$estimate
    }, n_model, n_human)
  )
act_cats$n<-act_cats$n_human+act_cats$n_model
print(act_cats, n=Inf)

sitting_standing_mismatch <- df.act %>%
  filter(
    str_detect(T5_actions, "SITTING|STANDING"),
    !str_detect(actions, "SITTING|STANDING") | is.na(actions)
  )

ssm2<-sitting_standing_mismatch[sitting_standing_mismatch$n_human_act == 1 & sitting_standing_mismatch$n_model_act == 1,]

###########################################
####### GLOBAL ERROR ANALYSIS #############
###########################################

###################################################
####### RQ1: Date / Error Correlation #############
###################################################

df<-read.csv("DATA_Illustration_IA_Evaluation_T0_T4.csv")

# remove NA
df<-df[which(df$T0 == "Yes"),]
df<-df[which(df$illustration_present == "Yes"),]

#Subset by model
df<-df[which(df$model == "gemini-2.5-flash"),]
df<-df[which(df$shot_type == "zeroshot"),]

meta<-read.csv("DATA_Illustration_IA_Annotations_Consensus_All.csv")

df <- df %>%
  left_join(meta %>% select(filename, decade), 
            by = c("image" = "filename"))

df_dated <- df %>% filter(!is.na(decade))

#T1
df_dated <- df_dated %>%
  mutate(
    error_T1 = mapply(function(mod, hum) {
      if (is.na(mod) | is.na(hum)) return(NA)
      mod_set <- str_trim(str_split(mod, "[;,]")[[1]])
      hum_set <- str_trim(str_split(str_remove_all(hum, "\\s*\\([^)]*\\)"), ",")[[1]])
      1 - length(intersect(mod_set, hum_set)) / length(union(mod_set, hum_set))
    }, characters, T1)
  )

#T2
df_dated <- df_dated %>%
  mutate(
    error_T2 = as.integer(scene_setting != T2)
  )

#T3
df_dated <- df_dated %>%
  mutate(
    error_T3 = mapply(function(mod, hum) {
      if (is.na(mod) | is.na(hum)) return(NA)
      mod_set <- str_trim(str_split(mod, "[;,]")[[1]])
      hum_set <- str_trim(str_split(str_remove_all(hum, "\\s*\\([^)]*\\)"), ",")[[1]])
      1 - length(intersect(mod_set, hum_set)) / length(union(mod_set, hum_set))
    }, objects, T3)
  )

df_dated <- df_dated %>%
  mutate(error_total = rowMeans(cbind(error_T1, error_T2, error_T3), na.rm = TRUE))

df_dated<-df_dated[df_dated$decade < 1950 & df_dated$decade > 1750,]
cor.test(df_dated$error_total, df_dated$decade, method = "spearman")
plot(df_dated$decade, df_dated$error_total)

ggplot(df_dated, aes(x = decade, y = error_total)) +
  geom_jitter(width = 2, height = 0, alpha = 0.3) +
  geom_smooth(method = "loess", se = TRUE, color = "steelblue") +
  labs(
    x = "Decade",
    y = "Error Score",
    title = "Model-Human Misalignment by Decade"
  ) +
  theme_minimal()

df_dated %>%
  group_by(decade) %>%
  summarise(
    mean_error = mean(error_total, na.rm = TRUE),
    n = n()
  ) %>%
  ggplot(aes(x = decade, y = mean_error, size = n)) +
  geom_point() +
  geom_smooth(method = "loess", se = TRUE, color = "steelblue") +
  labs(
    x = "Decade of Publication",
    y = "Mean Error Score"
  ) +
  theme_minimal() +
  theme(legend.position = "none")

df_dated <- df_dated %>%
  mutate(error_binary = as.integer(error_total > 0))

summary(glm(error_binary ~ decade, data = df_dated, family = binomial))

df_dated$n_model <- sapply(strsplit(df_dated$characters, "[;,]"), function(x) {
  if (all(is.na(x))) return(NA)
  x <- str_trim(x)
  if (all(x == "None")) return(0)
  sum(x != "" & x != "None")
})

df_dated$n_model_obj <- sapply(strsplit(df_dated$objects, "[;,]"), function(x) {
  if (all(is.na(x))) return(NA)
  x <- str_trim(x)
  if (all(x == "None")) return(0)
  sum(x != "" & x != "None")
})

df_dated <- df_dated %>%
  mutate(n_model_total = n_model + n_model_obj)

summary(lm(error_total ~ decade + n_model_total, data = df_dated))
summary(lm(error_total ~ decade, data = df_dated))

###################################################
####### RQ2: Similar Estimates? ###################
###################################################

##### RQ2: Corpus-level agreement #####

# T1: characters
t1_agreement <- cor.test(cats$prop_model, cats$prop_human, method = "pearson")
t1_mad <- mean(abs(cats$diff))

# T3: objects
t3_agreement <- cor.test(obj_cats$prop_model, obj_cats$prop_human, method = "pearson")
t3_mad <- mean(abs(obj_cats$diff))

# T2: scene setting — build a quick freq table first
df <- df %>%
  mutate(scene_setting = case_when(
    scene_setting == "Ambiguous" ~ "Both / Ambiguous",
    TRUE ~ scene_setting
  ))

t2_cats <- full_join(
  df %>% filter(!is.na(scene_setting)) %>% 
    count(scene_setting) %>% rename(category = scene_setting, n_model = n),
  df %>% separate_rows(T2, sep = ",") %>%
    mutate(T2 = str_trim(T2)) %>%
    filter(!is.na(T2), T2 != "", T2 != "NA") %>%
    count(T2) %>% rename(category = T2, n_human = n),
  by = "category"
) %>%
  replace_na(list(n_model = 0, n_human = 0)) %>%
  mutate(
    prop_model = n_model / sum(n_model),
    prop_human = n_human / sum(n_human),
    diff = prop_model - prop_human
  )
t2_agreement <- cor.test(t2_cats$prop_model, t2_cats$prop_human, method = "pearson")
t2_mad <- mean(abs(t2_cats$diff))

# T4: emotional intensity — correlate numeric scores directly
df <- df %>%
  mutate(
    emotional_intensity = as.numeric(emotional_intensity),
    T4_numeric = sapply(str_extract_all(T4, "^\\d|(?<=, )\\d"), function(x) {
      if (length(x) == 0 || all(is.na(x))) return(NA)
      mean(as.numeric(x))
    })
  )
t4_agreement <- cor.test(df$emotional_intensity, df$T4_numeric, 
                         method = "pearson", use = "complete.obs")

# Summary
cat("T1 (characters) - r:", round(t1_agreement$estimate, 3), "MAD:", round(t1_mad, 3), "\n")
cat("T2 (scene)      - r:", round(t2_agreement$estimate, 3), "MAD:", round(t2_mad, 3), "\n")
cat("T3 (objects)    - r:", round(t3_agreement$estimate, 3), "MAD:", round(t3_mad, 3), "\n")
cat("T4 (intensity)  - r:", round(t4_agreement$estimate, 3), "\n")


