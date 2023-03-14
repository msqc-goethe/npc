#!/usr/bin/env Rscript
library(ggplot2)
library(dplyr)
library(scales)

network_bytes <- function(papi_port_recv,papi_port_send){
	sum_bytes  <- papi_port_recv * 4 + papi_port_send * 4
	return(sum_bytes)
}

#Himeno XL 2 2 2
hm1_ops <- 43833.567657/2
hm1_bytes <- network_bytes(155560702,155559946)
hm1_fop <- (9037954800*291)/2
hm1_intens <- hm1_fop / hm1_bytes

#Himeno XL 4 4 4
hm2_ops <- 148353.345638/4
hm2_bytes <- network_bytes(396221147,396221147)
hm2_fop <- (9037954800*741)/4
hm2_intens <- hm2_fop / hm2_bytes

# Ceilings fuchs cluster
netpeak <- 6939.56
rpeak_sp  <- 836260.77
rpeak_dp  <- 418059.51

minor_breaks <- rep(1:9, 21)*(10^rep(-10:10, each=9))

roofline <- function(x) ifelse(rpeak_dp>x*netpeak,x*netpeak,rpeak_dp)
roofline_sp <- function(x) ifelse(rpeak_sp>x*netpeak,x*netpeak,rpeak_sp)

#hpcg 4proc 2 nodes
hc1_ops <- (8.21553 * 10^3)/2
hc1_bytes <- network_bytes(77766288,77766599)
hc1_fop <- 5.82831e+11 / 2
hc1_intens <- hc1_fop / hc1_bytes

#hpcg 8 proc 4 nodes
hc2_ops <- (16.395 * 10^3)/4
hc2_bytes <- network_bytes(156832664,156832621)
hc2_fop <- 1.16978e+12 / 4
hc2_intens <- hc2_fop / hc2_bytes
print(hc2_fop)
print(hc2_intens)

#hpcg 16 proc 8 nodes
hc3_ops <- (32.6517 * 10^3)/8
hc3_bytes <- network_bytes(156886095,156886445)
hc3_fop <- 2.34367e+12 / 8
hc3_intens <- hc3_fop / hc3_bytes
print(hc3_intens)
xdata <- 10^-1:10^4
print(length(xdata))
ydata  <- sapply(xdata,roofline)
gdata  <- data.frame(xdata=xdata,ydata=ydata)

res <- data.frame(Benchmark=c("n=2","n=4","n=2","n=4"),
				  Intensity=c(hm1_intens,hm2_intens,hc1_intens,hc2_intens),
				  Performance=c(hm1_ops,hm2_ops,hc1_ops,hc2_ops),
				  Tag=c("HimenoXL","HimenoXL","HPCG","HPCG")) 

res <-  mutate(res,Legend = paste(Benchmark,Tag,sep=","))
print(res)

p <- ggplot(data = gdata,aes(x = xdata,y = ydata)) +
	stat_function(fun=roofline_sp,color='black',linetype="dashed") +
	annotate("text",x = 3, y = 10^4.5, label = "FDR Bandwidth 6.93 GB/s",angle=47, size=2) +
	annotate("text",x = 1000, y = rpeak_sp + 200500, label = "SP Performance", size=2) +
	annotate("text",x = 1000, y = rpeak_dp + 100000, label = "DP Performance", size=2) +
	geom_line() +
	geom_point(data = res,aes(x = Intensity, y = Performance, shape = Benchmark, color = Tag),size=1.5) +
	scale_x_continuous(trans = log10_trans(),
	                         breaks = trans_breaks("log10", function(x) 10^x),
							 minor_breaks = minor_breaks,
	                         labels = trans_format("log10", math_format(10^.x))) +
	scale_y_continuous(trans = log10_trans(),
	                         breaks = trans_breaks("log10", function(x) 10^x),
							 minor_breaks = minor_breaks,
	                         labels = trans_format("log10", math_format(10^.x))) +

	xlab(label='Operational Intensity [FLOP/Byte]') + ylab(label='Performance [MFLOPS]') +
	annotation_logticks(size = 0.25) +
	labs(shape='',color='') +
	theme_bw() +
	# theme_bw(base_size = 10) +
	theme(legend.position = "top", axis.title = element_text(size=8),legend.text = element_text(size=8))
	# theme(legend.position = "top",axis.text = element_text(size=16) ,axis.title = element_text(size=16), legend.text = element_text(size=14),
	# strip.text.y = element_text(size=14),
	# )
# ggsave('roofline.pdf')
ggsave('roofline.pdf',width=3.6,height=3,units="in",dpi=300)
