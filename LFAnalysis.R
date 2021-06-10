

###########

# read in the data file and name the columns
alldata = read.table("alldata-converted.txt", header=F)
names(alldata) = c("subj", "cond", "p_flip", "trial_type", "trial", "a_reward", "b_reward", "res", "rew", "RT", "n_missed")



###########################################################################
# this part adds two new columns to the data, one that tells if they explored in that trial
# and one that tells if they chose the best option

alldata$explore <- NULL
alldata$best <- NULL

highest_seen <- 20
for (i in 1:length(alldata$subj)) {
	
	if (alldata[i,]$trial == 1) {
		alldata$explore[i] <- 0
		highest_seen <- 20
	} 
	else if (alldata[i,]$rew == highest_seen | alldata[i,]$rew == highest_seen + 20 ) {
		alldata$explore[i] <- 0
		highest_seen <- alldata[i,]$rew
	}
	else {
		alldata$explore[i] <- 1
		if (alldata[i,]$rew > highest_seen) {
			highest_seen <- alldata[i,]$rew
		}
	}
	
	if (alldata[i,]$rew == max(alldata[i,]$a_reward, alldata[i,]$b_reward)) {
		alldata$best[i] <- 1
	}
	else { alldata$best[i] <- 0}
	
}

###########################################################################
# EXCLUSIONS
###########################################################################
# for removing subjects that you want to exclude from further analyses
alldata <- alldata[alldata$subj != 11111,] # replace with subject number to exclude
#alldata <- alldata[alldata$subj != 22222,]

#########################################################
# MAIN behavioral measures

# exploration rate by subject
explore_by_subj = tapply(alldata$explore, alldata$subj, mean)
explore_by_subj
# mean and standard deviation
mean(explore_by_subj)
sd(explore_by_subj)

# task performance (proportion of trials they chose the actual best option) by subject
performance_by_subj = tapply(alldata$best, alldata$subj, mean)
performance_by_subj 
# mean and standard deviation
mean(performance_by_subj)
sd(performance_by_subj)


#######################################################################
# histograms
#######################################################################

# plot some histograms of performance and exploration rate
par(mfrow=c(1,2))

hist(explore_by_subj,
	main = "Exploration rate",
	xlab="Exploration rate",
	col = "orange", xlim=c(0,0.6),
	breaks = c(0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6), 
	cex.lab = 1.4, cex.axis=1.2)

#quartz()
hist(performance_by_subj,
	main = "Performance",
	xlab="Proportion best option selected",
	col="blue", xlim=c(0.5,1.0), 
	breaks = c(0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0), 
	cex.lab = 1.4, cex.axis=1.2)


##########################################################################
# BY BLOCK ANALYSES
##########################################################################

# make a new columan that divides the data up into blocks of 50 trials
alldata$block <- floor( (alldata$trial-1)/50 + 1)

# get exploration rate and performance by block per subject
explore_by_block = tapply(alldata$explore, list(alldata$subj, alldata$block), mean)
performance_by_block = tapply(alldata$best, list(alldata$subj, alldata$block), mean)

explore_by_block
performance_by_block

# get block means
explore_means <- apply(explore_by_block, 2, mean)
performance_means <- apply(performance_by_block, 2, mean)

# get standard deviations
explore_sds <- apply(explore_by_block, 2, sd)
performance_sds <- apply(performance_by_block, 2, sd)

# number of subjects
Nsubjs <- length(unique(alldata$subj))

# standard errors
explore_ses <- explore_sds/sqrt(Nsubjs)
performance_ses <- performance_sds/sqrt(Nsubjs)

# plot by block means
par(mfrow=c(1,2))
x <- seq(length(explore_means))
plot(explore_means, type = 'l', main =  "Exploration rate by block", 
			 xlab = "block", ylab = "exploration rate", ylim=c(0,1))
segments(x, explore_means+explore_ses, x, explore_means-explore_ses)		 
			 
plot(performance_means, type = 'l', main =  "Performance by block", 
			 xlab = "block", ylab = "proportion best option selections", ylim=c(0,1))	
segments(x, performance_means+performance_ses, x, performance_means-performance_ses)			 

####################################################################
# MODEL ANALYSES
####################################################################

# read in the model fit output files
RL_data <- read.table('RL_fits.txt', header=F)
names(RL_data) <- c('subj', 'nllh', 'BIC', 'SM_parameter')

baseline_data <- read.table('baseline_fits.txt', header=F)
names(baseline_data) <- c('subj', 'nllh', 'BIC', 'prob_A')

IA_data <- read.table('IA_fits.txt', header=F)
names(IA_data) <- c('subj', 'nllh', 'BIC', 'p_flip', 'SM_parameter')

belief_data <- read.table('belief_fits.txt', header=F)
names(belief_data) <- c('subj', 'nllh', 'BIC', 'p_flip', 'SM_parameter')

# combine it all into one data file
combined_data <- NULL

combined_data$subj <- RL_data$subj
combined_data$RL_BIC <- RL_data$BIC
combined_data$baseline_BIC <- baseline_data$BIC
combined_data$IA_BIC <- IA_data$BIC
combined_data$belief_BIC <- belief_data$BIC
combined_data <- as.data.frame(combined_data)

# see which model was best (lowest BIC)
combined_data$RL_best <- as.numeric((combined_data$RL_BIC < combined_data$baseline_BIC) &
						  (combined_data$RL_BIC < combined_data$IA_BIC) &
						  (combined_data$RL_BIC < combined_data$belief_BIC))

combined_data$baseline_best <- as.numeric((combined_data$baseline_BIC < combined_data$RL_BIC) &
						  		(combined_data$baseline_BIC < combined_data$IA_BIC) &
						  		(combined_data$baseline_BIC < combined_data$belief_BIC))
						  		
combined_data$IA_best <- as.numeric((combined_data$IA_BIC < combined_data$RL_BIC) &
						  (combined_data$IA_BIC < combined_data$baseline_BIC) &
						  (combined_data$IA_BIC < combined_data$belief_BIC))
						  
combined_data$belief_best <- as.numeric((combined_data$belief_BIC < combined_data$baseline_BIC) &
						  (combined_data$belief_BIC < combined_data$IA_BIC) &
						  (combined_data$belief_BIC < combined_data$RL_BIC))

# check if IA fits better than the RL model (ignoring the other models)						  
combined_data$IA_over_RL <- as.numeric(combined_data$IA_BIC < combined_data$RL_BIC)

combined_data

# number of participants best fit by each model
total_RL_best_fit <- sum(combined_data$RL_best)
total_RL_best_fit

total_belief_best_fit <- sum(combined_data$belief_best)
total_belief_best_fit

total_IA_best_fit <- sum(combined_data$IA_best)
total_IA_best_fit

total_baseline_best_fit <- sum(combined_data$baseline_best)
total_baseline_best_fit

# number of participants IA fits better than the RL model 
sum(combined_data$IA_over_RL)

