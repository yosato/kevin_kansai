library(readr)
onbin_data <- read_csv("onbin_data.csv")
View(onbin_data)

#subset the data to include the non-opaque environment only
onbin_non_opaque <- onbin_data[onbin_data$opaque==0,]

#subset the data to include the opaque environment only
onbin_opaque <- onbin_data[onbin_data$opaque==1,]

library(lme4)
#(1 | abc) means take abc as a random effect

###the non-opaque data###
#model 1; test age, gender, and speech style; result: only speech style is significant
model1 <- glmer(onbin ~ age + gender + speech_style + (1|speaker) + (1|word), data = onbin_non_opaque, family = binomial, control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)
summary(model1)

#model 2; add in adjacent, f_pos; result both adjacent and f_pos significant
model2 <- glmer(onbin ~ speech_style + adjacent + f_pos + (1|speaker) + (1|word), data = onbin_non_opaque, family = binomial, control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)
summary(model2)

#models 3a, 3b, 3c, 3d; test in wFreq, mFreq, wpFreq, and mpFreq separately as models 3a 3b 3c 3d respectively
model3a <- glmer(onbin ~ speech_style + adjacent + f_pos + wFreq + (1|speaker) + (1|word), data = onbin_non_opaque, family = binomial, control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)
summary(model3a)
model3b <- glmer(onbin ~ speech_style + adjacent + f_pos + mFreq + (1|speaker) + (1|word), data = onbin_non_opaque, family = binomial, control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)
summary(model3b)
model3c <- glmer(onbin ~ speech_style + adjacent + f_pos + wpFreq + (1|speaker) + (1|word), data = onbin_non_opaque, family = binomial, control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)
summary(model3c)
model3d <- glmer(onbin ~ speech_style + adjacent + f_pos + mpFreq + (1|speaker) + (1|word), data = onbin_non_opaque, family = binomial, control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)
summary(model3d)

#log likelihood results for the four models (closer to zero = better result)
#model 3a: -3467.4
#model 3b: -3376.2
#model 3c: -3296.9
#model 3d: -3242.0 *** best model
#result: keep mpFreq in the model

#models 4a, 4b, 4c, 4d; test in wpfp, wpbp, mpfp, and mpbp separately as models 4a 4b 4c 4d respectively
model4a <- glmer(onbin ~ speech_style + adjacent + f_pos + mpFreq + wpfp + (1|speaker) + (1|word), data = onbin_non_opaque, family = binomial, control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)
summary(model4a)
model4b <- glmer(onbin ~ speech_style + adjacent + f_pos + mpFreq + wpbp + (1|speaker) + (1|word), data = onbin_non_opaque, family = binomial, control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)
summary(model4b)
model4c <- glmer(onbin ~ speech_style + adjacent + f_pos + mpFreq + mpfp + (1|speaker) + (1|word), data = onbin_non_opaque, family = binomial, control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)
summary(model4c)
model4d <- glmer(onbin ~ speech_style + adjacent + f_pos + mpFreq + mpbp + (1|speaker) + (1|word), data = onbin_non_opaque, family = binomial, control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)
summary(model4d)


#log likelihood results for the four models (closer to zero = better result)
#model 4a: -3168.7
#model 4b: -3231.0, wpbp not significant
#model 4c: -3073.4 *** best model
#model 4d: -3106.9
#result: keep mpfp in the model

###the opaque data###
#model 5; test age, gender, and speech style; result: only speech style is significant
model5 <- glmer(onbin ~ age + gender + speech_style + (1|speaker) + (1|word), data = onbin_opaque, family = binomial, control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)
summary(model5)

#model 6; add in adjacent, f_pos; result both adjacent and f_pos significant
model6 <- glmer(onbin ~ speech_style + adjacent + f_pos + (1|speaker) + (1|word), data = onbin_opaque, family = binomial, control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)
summary(model6)

#models 7a, 7b, 7c, 7d; test wFreq, mFreq, wpFreq, and mpFreq separately as models 7a 7b 7c 7d respectively
model7a <- glmer(onbin ~ speech_style + adjacent + f_pos + wFreq + (1|speaker) + (1|word), data = onbin_opaque, family = binomial, control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)
summary(model7a)
model7b <- glmer(onbin ~ speech_style + adjacent + f_pos + mFreq + (1|speaker) + (1|word), data = onbin_opaque, family = binomial, control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)
summary(model7b)
model7c <- glmer(onbin ~ speech_style + adjacent + f_pos + wpFreq + (1|speaker) + (1|word), data = onbin_opaque, family = binomial, control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)
summary(model7c)
model7d <- glmer(onbin ~ speech_style + adjacent + f_pos + mpFreq + (1|speaker) + (1|word), data = onbin_opaque, family = binomial, control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)
summary(model7d)

#log likelihood results for the four models (closer to zero = better result)
#model 7a: -433.4
#model 7b: -428.4
#model 7c: -365.4
#model 7d: -356.9 *** best model
#result: keep mpFreq in the model

#models 8a, 8b, 8c, 8d; test in wpfp, wpbp, mpfp, and mpbp separately as models 8a 8b 8c 8d respectively
model8a <- glmer(onbin ~ speech_style + adjacent + f_pos + mpFreq + wpfp + (1|speaker) + (1|word), data = onbin_opaque, family = binomial, control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)
summary(model8a)
model8b <- glmer(onbin ~ speech_style + adjacent + f_pos + mpFreq + wpbp + (1|speaker) + (1|word), data = onbin_opaque, family = binomial, control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)
summary(model8b)
model8c <- glmer(onbin ~ speech_style + adjacent + f_pos + mpFreq + mpfp + (1|speaker) + (1|word), data = onbin_opaque, family = binomial, control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)
summary(model8c)
model8d <- glmer(onbin ~ speech_style + adjacent + f_pos + mpFreq + mpbp + (1|speaker) + (1|word), data = onbin_opaque, family = binomial, control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)
summary(model8d)


#log likelihood results for the four models (closer to zero = better result)
#model 8a: -211.2, wpfp sign.
#model 8b: -277.2, wpbp not sign.
#model 8c: -105.0, mpfp sign., *** best model
#model 8d: -352.9, mpbp not sign.
#result: keep mpfp in the model