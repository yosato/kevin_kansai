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
#model 4d: model failed to converge
#result: keep mpfp in the model