library(readr)
onbin_data <- read_csv("onbin_data.csv")
View(onbin_data)

#subset the data to include the traditional environment only
onbin_trad_only <- onbin_data[onbin_data$traditional==1,]

#subset the data to include the non-traditional environment only
onbin_non_trad_only <- onbin_data[onbin_data$traditional==0,]

#subset the data to include the neutralized environment only
onbin_neutral_only <- onbin_data[onbin_data$neutralized==1,]

library(lme4)
#(1 | abc) means take abc as a random effect
m_test <- glmer(onbin ~ age + gender + speech_style + (1 | speaker), data = onbin_trad_only, family = binomial, control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)
summary(m_test)


m_test <- glmer(onbin ~ speech_style + location + mpFreq + (1 | speaker), data = onbin_trad_only, family = binomial, control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)
m_test <- glmer(onbin ~ age + + gender + speech_style + (1 | speaker), data = onbin_non_trad_only, family = binomial, control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)
m_test <- glmer(onbin ~ speech_style + mpFreq + (1 | speaker), data = onbin_trad_only, family = binomial, control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)
m_test <- glmer(onbin ~ speech_style + mpbp + (1 | speaker), data = onbin_trad_only, family = binomial, control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)
m_test <- glmer(onbin ~ speech_style + mpbp + (1 | speaker), data = onbin_non_trad_only, family = binomial, control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)
m_test <- glmer(onbin ~ speech_style + mpfp + (1 | speaker), data = onbin_neutral_only, family = binomial, control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)
m_test <- glmer(onbin ~ speech_style + mpFreq + mpfp + mpbp + (1 | speaker), data = onbin_trad_only, family = binomial, control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)





