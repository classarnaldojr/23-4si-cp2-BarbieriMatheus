import cv2

esquerda_papel = cv2.imread('esquerda-papel.png', 0)
esquerda_tesoura = cv2.imread('esquerda-tesoura.png', 0)
esquerda_pedra = cv2.imread('esquerda-pedra.png', 0)

PAPEL = "papel"
TESOURA = "tesoura"
PEDRA = "pedra"

ESQUERDA = "esquerda"
DIREITA = "direita"
EMPATE = "empate"

direita_papel = cv2.rotate(esquerda_papel, cv2.ROTATE_180)
direita_tesoura = cv2.rotate(esquerda_tesoura, cv2.ROTATE_180)
direita_pedra = cv2.rotate(esquerda_pedra, cv2.ROTATE_180)

threshold_esquerda_papel = 79733248.0
threshold_esquerda_tesoura = 53568512.0
threshold_esquerda_pedra = 4059136.0

threshold_direita_papel = 79661056.0
threshold_direita_tesoura = 1561088.0
threshold_direita_pedra = 5630976.0

salva_gesto_esquerda = ""
salva_gesto_direita = ""
resultado_pontuacao = (0, 0)

count_frame = 0

def calculaResultado(gesto_esquerda, gesto_direita):
    if (gesto_esquerda == gesto_direita):
        return EMPATE

    if (gesto_esquerda == PAPEL):
        if (gesto_direita == TESOURA):
            return DIREITA
        if (gesto_direita == PEDRA):
            return ESQUERDA

    if (gesto_esquerda == TESOURA):
        if (gesto_direita == PAPEL):
            return ESQUERDA
        if (gesto_direita == PEDRA):
            return DIREITA

    if (gesto_esquerda == PEDRA):
        if (gesto_direita == PAPEL):
            return DIREITA
        if (gesto_direita == TESOURA):
            return ESQUERDA
        
def desenhaTexto(img, text, position):
    font                   = cv2.FONT_HERSHEY_SIMPLEX
    bottomLeftCornerOfText = position
    fontScale              = 1.2
    fontColor              = (0,0,0)
    thickness              = 2
    lineType               = 2

    cv2.putText(img, text, 
        bottomLeftCornerOfText, 
        font, 
        fontScale,
        fontColor,
        thickness,
        lineType)
    
def salvaPlacar(resultado):
    global resultado_pontuacao
    if (resultado == EMPATE):
        return
    
    if (resultado == ESQUERDA):
        resultado_pontuacao = (resultado_pontuacao[0] + 1, resultado_pontuacao[1])
        return

    if (resultado == DIREITA):
        resultado_pontuacao = (resultado_pontuacao[0], resultado_pontuacao[1] + 1)
        return
    
def comparaGestoAnteriorEPosterior(gesto_esquerda, gesto_direita):
    global salva_gesto_esquerda
    global salva_gesto_direita
    return gesto_esquerda == salva_gesto_esquerda and gesto_direita == salva_gesto_direita

def desenhaRetangulo(frame, min_loc, template):
    width = template.shape[1]
    height = template.shape[0]

    position_initial = (min_loc[0],min_loc[1])
    position_final = (min_loc[0] + width,min_loc[1] + height)
    color = (127,255,255)
    espessura = 2
    cv2.rectangle(frame, position_initial, position_final, color, espessura)
    return

def encontraTemplate(frame, template, threshold):
    res = cv2.matchTemplate(frame, template, cv2.TM_SQDIFF)
    min_val, _, min_loc, _ = cv2.minMaxLoc(res)

    if (min_val > threshold):
        return
    return min_loc

def encontraMaoEDesenhaRetangulo(frame, frame_gray, template, threshold, nome, lado):
    min_loc = encontraTemplate(frame_gray, template, threshold)
    if min_loc:
        desenhaRetangulo(frame, min_loc, template)
        desenhaTexto(frame, "Jogador da " + lado, (min_loc[0], min_loc[1] + 300))
        desenhaTexto(frame, nome, (min_loc[0], min_loc[1] + 350))
        return nome

def lidaComMaoEsquerda(img, img_gray):
    gesto_papel = encontraMaoEDesenhaRetangulo(img, img_gray, esquerda_papel, threshold_esquerda_papel, PAPEL, "esquerda")
    gesto_tesoura = encontraMaoEDesenhaRetangulo(img, img_gray, esquerda_tesoura, threshold_esquerda_tesoura, TESOURA, "esquerda")
    gesto_pedra = encontraMaoEDesenhaRetangulo(img, img_gray, esquerda_pedra, threshold_esquerda_pedra, PEDRA, "esquerda")
    return gesto_papel or gesto_tesoura or gesto_pedra

def lidaComMaoDireita(img, img_gray):
    gesto_papel = encontraMaoEDesenhaRetangulo(img, img_gray, direita_papel, threshold_direita_papel, PAPEL, "direita")
    gesto_tesoura = encontraMaoEDesenhaRetangulo(img, img_gray, direita_tesoura, threshold_direita_tesoura, TESOURA, "direita")
    gesto_pedra = encontraMaoEDesenhaRetangulo(img, img_gray, direita_pedra, threshold_direita_pedra, PEDRA, "direita")
    return gesto_papel or gesto_tesoura or gesto_pedra


def encontraGestos(img):
    global salva_gesto_direita
    global salva_gesto_esquerda
    global resultado_pontuacao

    img_gray = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2GRAY)
    gesto_esquerda = lidaComMaoEsquerda(img, img_gray)
    gesto_direita = lidaComMaoDireita(img, img_gray)

    resultado = calculaResultado(gesto_esquerda, gesto_direita)

    gestoAnteriorEIgual = comparaGestoAnteriorEPosterior(gesto_esquerda, gesto_direita)
    if not gestoAnteriorEIgual:
        salva_gesto_esquerda = gesto_esquerda
        salva_gesto_direita = gesto_direita
        salvaPlacar(resultado)

    desenhaTexto(
        img, 
        "Placar      " + str(resultado_pontuacao[0]) + " | " + str(resultado_pontuacao[1]),
        (750, 150)
    )
    desenhaTexto(
        img, 
        EMPATE if resultado == EMPATE else "Jogador da " + resultado + " venceu",
        (750, 200)
    )

    return img

cv2.namedWindow("preview")
vc = cv2.VideoCapture("pedra-papel-tesoura.mp4")

if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
else:
    rval = False

while rval:
    count_frame += 1

    if (count_frame == 30):
      img = encontraGestos(frame)
      cv2.imshow("preview", img)
      count_frame = 0

    rval, frame = vc.read()
    key = cv2.waitKey(20)
    if key == 27: # exit on ESC
        break

cv2.destroyWindow("preview")
vc.release()
