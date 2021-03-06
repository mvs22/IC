from matplotlib import pyplot as plt
import numpy as np
import random
import json
import math
import cv2
import os

save_json = {}

#Atualmente estas funções não estão em uso
'''
def area(contornos):
    a = cv2.contourArea(contornos)
    if a == None:
        a = 0.0
    return a

def comprimento(contornos):
    c = cv2.arcLength(contornos,True)
    if c == None:
        c = 0.0
    return c

def largura(contornos):
    x,y,w,h = cv2.boundingRect(contornos)
    if w == None:
        w = 0.0
    return w

def altura(contornos):
    x,y,w,h = cv2.boundingRect(contornos)
    if h == None:
       h = 0.0
    return h

def circularidade(contornos):
    c =(4*math.pi*cv2.contourArea(contornos))/((cv2.arcLength(contornos,True)**2))
    if c == None:
        c = 0.0
    return c

'''

#Verificada e deixando apenas em função da erosao
def reducao_ruido(num,imagem):	
	kernel = np.ones((12,12),np.uint8)
	
	erosao = cv2.erode(imagem,kernel,iterations = 1)

	pasta = "Imagens_Selecionadas_Analise_Geral"
	salvar(pasta,erosao, str(num) + "_Erosao" )

	return erosao

#Teste de um outro fluxo (o original) , para geração de informações sobre a imagem
def transform_image(img):
	thresh = 127
	maxValue = 255
	kernel = np.ones((5,5),np.uint8)
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	ret, th = cv2.threshold(gray,thresh,maxValue,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
	opening = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)
	erosion = cv2.erode(opening,kernel,iterations = 1)
	erosion = cv2.bitwise_not(erosion)
	contours, hierarchy = cv2.findContours(erosion, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

	a = cv2.drawContours(img,contours,-1,(255,0,0),3)
	mostrar_imagem(a)
	print("CONTORNOS:", contours)
	print("HIERARCHY:",hierarchy)
	
	return 0

#Utiliza a função CANNY para transformar uma imagem em GRAY SCALE para uma imgem BINARIZADA (Transforma em preto < X e branco em > x)
def encontrando_contornos(imagem):
	imagem2 = cv2.Canny(imagem,100,200) #Verificar a função da forma cv2.Canny(imagem) somente
	return imagem2

#Função que retorna a circularidade de um contorno gerado (IMPORTANTE VERIFICAR A CIRCULARIDADE PARA CONTORNOS IMCOMPLETOS)
def circularidade(contornos):
	try:
		c = ((4*math.pi*cv2.contourArea(contornos))/(cv2.arcLength(contornos,True)**2))
		if (c == None):
			c = 0.0
		return c
	except:
		return 0.0

#Função responsavel por pegar o DESVIO PADRAO do contorno (VERIFICAR COMO ELA REALMENTE FUNCIONA)
def standard_deviation(contornos):
	try:
		(means, std) = cv2.meanStdDev(contornos)
		for k in std:
			for m in k:
				std = m
		if std == None:
			std = 0.0
		return std
	except:
		return 0.0

#Esta função tem como objetivo RETORNAR um TRUE ou FALSE (1,0), para a função DEFININDO CARACTERISTICAS,
#		informando se os PONTOS EXTREMOS dos CONTORNOS são aceitaveis, 
#Ela também faz o corte da imagem, para salvar somente a REGIÃO DE CONTORNO PASSADA, para melhor analise, porém,
#		se essa funcionalidade não for mais utilizada, está função pode ser transcrita em DEFININDO CARACTERISTICAS e EXCLUIDA
def reanalizando_contornos(imagem,novos_contornos,num_imagem,num):
	listaX=[]
	listaY=[]

	#print ("VALORES: ")
	for i in range(0,4):
		x,y = novos_contornos[i]
		#print (x,y)
		listaX.append(y)
		listaY.append(x)
	
	x1,x2 = min(listaX),max(listaX)
	y1,y2 = min(listaY),max(listaY)

	if (x1 != x2 and y1 != y2 and x1 >= 0 and x2 >= 0 and y1 >= 0 and y2 >= 0):
		imagem_fatia = imagem[x1:x2,y1:y2] #Aqui é feito um recorte em relação a area do contorno analisado
		#mostrar_imagem(imagem_fatia)

		#Esse calculo é feito para que a imagemFatia contenha uma area significativa em relação a imagem original
		height, width = imagem_fatia.shape[:2]
		area_total = 256*512
		area_subImagem = height * width 
		area_final = (area_subImagem / area_total) 

		#print (area_final)
		#mostrar_imagem(imagem_fatia)

		#VERIFICAR A POSSIBILIDADE DO RESIZE NA IMAGEM "28/10/2019 00:00"
		#res = cv2.resize(imagem_fatia,(10*width, 10*height), interpolation = cv2.INTER_CUBIC)
		#mostrar_imagem(res)

		#if (area_final >= 0.01):
		#pasta = '3_SubImagens'
		#nome = str(num_imagem) + '_' + str(num)
		#salvar(pasta,imagem_fatia,nome)
		return 1
	else:
		print("FORA")		
		imagem_fatia = 0

	return 0

#Está função tem como objetivo pegar a IMAGEM ORIGINAL, a imagem gerada na função CANNY com seus CONTORNOS, 
#		assim como informaçoes de controle e salvamento dos arquivos (NUM IMAGEM e LISTA - que poderá ser substituida por um JSON)
def definindo_caracteristicas(imagem, imagem_canny,num_imagem,lista):
	num = 1
	
	contornos, hierarquia = cv2.findContours(imagem_canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
	imagem_contornosQuadrados = imagem.copy()

	for i in range(len(contornos)):
		teste = contornos[i] 
		imagem_contorno = imagem.copy()
		imagem_quadrado = imagem.copy()

		quadrado = cv2.minAreaRect(teste)
		novos_contornos = cv2.boxPoints(quadrado)
		novos_contornos = np.int0(novos_contornos)

		#VERIFICAR A RETIRADA DA CONDIÇÃO DE "largura e altura" 28/10/2019 23:50
		#if (area(novos_contornos) >  100 and largura(novos_contornos) > 15 and altura(novos_contornos) > 15):
		#print ("A1: %f | P1: %f | W1: %f | H1: %f" %(area(teste),comprimento(teste),largura(teste),altura(teste)))
		#print ("A2: %f | P2: %f | W2: %f | H2: %f" %(area(novos_contornos),comprimento(novos_contornos),largura(novos_contornos),altura(novos_contornos)))

		#cv2.drawContours(imagem_contorno,[teste],0,(255,0,0),3)
		#cv2.drawContours(imagem_quadrado,[novos_contornos],0,(0,255,0),3)

		#mostrar_imagem(imagem_contorno)
		#mostrar_imagem(imagem_quadrado)


		if (reanalizando_contornos(imagem,novos_contornos,num_imagem,num) == 1):

			cv2.drawContours(imagem_contornosQuadrados,[novos_contornos],0,(0,0,255),3)
			#pasta = '2_Tratadas'
			pasta = "Imagens_Selecionadas_Individuais"
			nome = str(num_imagem) + '_' + str(num)
			salvar(pasta,cv2.drawContours(imagem_quadrado,[novos_contornos],0,(0,255,0),3),nome)
			#nome = 0
			lista.append([novos_contornos.tolist(),num_imagem,num,round(circularidade(novos_contornos),2),round(standard_deviation(novos_contornos),2)])
			save_json[num] = {"limites":novos_contornos.tolist(),
         						"circularidade":round(circularidade(novos_contornos),2),
        						"desvio_padrao":round(standard_deviation(novos_contornos),2)
							 }
							
			num +=1

	imagem_contornosCanny = imagem.copy()
	cv2.drawContours(imagem_contornosCanny,contornos,-1,(0,255,255),3)

	pasta = "Imagens_Selecionadas_Analise_Geral"

	salvar(pasta,imagem_canny, str(num_imagem) + '_Canny' )
	salvar(pasta,imagem_contornosQuadrados, str(num_imagem) + '_Regioes' )
	salvar(pasta,imagem_contornosCanny, str(num_imagem) + '_Contornos')

	return imagem,num,lista

#Mostrar apenas uma imagem 
def mostrar_imagem(imagem):

	cv2.imshow('Imagem',imagem)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

	return 0

#Mostrar varias imagens
def mostrar_imagens(imagem1,imagem2,imagem3,imagem4):
	plt.subplot(221), plt.imshow(imagem1, 'gray')
	plt.subplot(222), plt.imshow(imagem2,'gray')
	plt.subplot(223), plt.imshow(imagem3, 'gray')
	plt.subplot(224), plt.imshow(imagem4,'gray')
	plt.show()

	return 0

#Salvar imagens (ESTA FUNÇÃO PODE MELHORAR E SE TORNAR MAIS GENERICA EM SEU PATH DE DESTINO)
def salvar(pasta,imagem,nome):
	destino = "C:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\Imagens_IC\\Destino_Imagens\\"
	
	final = destino + pasta + '\\' + nome + '.png'
	cv2.imwrite(final,imagem)

	return 0

#Função de teste para analise de REDUÇÃO DE RUIDO nas imagens e uma melhor tentativa de DIFERENCIAR as vias dos BURACOS
def thresh_callback(val,src_gray):
	threshold = val
	print("THRESHOLD")
	# Detect edges using Canny
	canny_output = cv2.Canny(src_gray, threshold, (threshold * 2 ) + 55)
	mostrar_imagem(canny_output)

	# Find contours
	contours, hie = cv2.findContours(canny_output, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

	# Find the convex hull object for each contour
	hull_list = []
	for i in range(len(contours)):
		hull = cv2.convexHull(contours[i])
		hull_list.append(hull)

	# Draw contours + hull results
	drawing = np.zeros((canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)
	drawing_2 = np.zeros((canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)
	for i in range(len(contours)):
		color = (random.randint(0,256),random.randint(0,256),random.randint(0,256))
		cv2.drawContours(drawing, contours, i, color)
		cv2.drawContours(drawing_2, hull_list, i, color)

	# Show in a window
	mostrar_imagens(src_gray,canny_output,drawing,drawing_2)


if __name__ == "__main__":

	#h = "C:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Potholes_Cracks_Patches\\Source\\Cropped_Resized_Data\\"
	#origem = "C:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\FEATURES\\"
	#origem = '/media/study/Arquivos HD 2/Aprender/Areas de Atuacao/Processamento de Imagens/Imagens/Origem/'
	#origem2 = '/media/study/Arquivos HD 2/Aprender/Areas de Atuacao/Processamento de Imagens/Imagens/Origem_Fake/'
	#destino = '/media/study/Arquivos HD 2/Aprender/Areas de Atuacao/Processamento de Imagens/Imagens/Imagens_F/'
	#openn = 'C:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\Imagens_F\\'
	#openn = '/media/study/Arquivos HD 2/Aprender/Areas de Atuacao/Processamento de Imagens/Imagens/Imagens_F/'
	#destino = 'C:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\Imagens_F\\'
	#origem2 = 'C:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\Origem_Fake\\'
	
	origem = "C:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\Imagens_IC\\Origem_Imagens\\Imagens_Google_Maps\\"
	destinoPosicoes = "C:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\Imagens_IC\\Destino_Imagens\\Arquivo_Posicoes\\"

	for _, _, arquivo in os.walk(origem):
		pass

	for img in arquivo:
		lista = [[]]
		
		i = int(img.split('.')[0])
		imagem = cv2.imread(origem+img)

		#mostrar_imagem(imagem)
		
		#Redimensionando a imagem
		#a = cv2.resize(imagem,(512,512))
		#b = a[150:310,50:462]
		#c = cv2.resize(b,(512,512))
		#imagem = c[256:512,0:512]
		imagem = imagem[256:512,0:512]
		#mostrar_imagem(imagem)

		#salvar('1_Especial',imagem,str(i)+ '_Cut')
		
		imagem_cinza = cv2.cvtColor(imagem,cv2.COLOR_RGB2GRAY)
		#mostrar_imagem(imagem_cinza)

		#salvar('1_Especial',imagem_cinza,str(i)+"_Gray")
		salvar('Imagens_Selecionadas_Analise_Geral',imagem_cinza,str(i)+"_Gray")

		imagem_tratada2 = reducao_ruido(i,imagem_cinza)
		#mostrar_imagens(imagem_cinza,imagem_tratada2,imagem_tratada3,imagem_tratada4)
		#mostrar_imagem(imagem_tratada2)
		
		#thresh_callback(100,imagem_tratada2)
		
		#imagem_canny = encontrando_contornos(imagem_tratada)
		imagem_canny2 = encontrando_contornos(imagem_tratada2)
		#imagem_canny3 = encontrando_contornos(imagem_tratada3)
		#mostrar_imagens(imagem_cinza,imagem_canny,imagem_canny2,imagem_canny3)
		#mostrar_imagem(imagem_canny)

		#imagem_finalizada,quant_img_salvas,lista = definindo_caracteristicas(imagem,imagem_canny,i,lista)
		imagem_finalizada2,quant_img_salvas2,lista = definindo_caracteristicas(imagem,imagem_canny2,i,lista)
		#imagem_finalizada3,quant_img_salvas3,lista = definindo_caracteristicas(imagem,imagem_canny3,i,lista)
		#mostrar_imagens(imagem_cinza,imagem_canny,imagem_canny2,imagem_canny3)
			
		#mostrar_imagem(imagem_finalizada)

		print("TERMINOU")

		with open(destinoPosicoes + "STRUCT_BASE_" + str(i) + ".json", 'w') as json_file:
			json.dump(save_json, json_file)
		
		#try:
		#	#print(lista)
		#	arq = open(destino + "0_Listas_Posicoes\\"+ "lista" +str(i) + ".txt", 'w')
		#	saida = str(lista[1:])
		#	if i == 2:
		#		print(lista[1:])
		#	arq.write(saida)
		#	arq.close()

		#except Exception as e:                
		#	print ("ERRO:",img)
		#	pass