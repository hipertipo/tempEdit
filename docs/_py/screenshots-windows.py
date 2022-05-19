imgs = [
    '/Users/gferreira/Desktop/Screen Shot 2022-05-18 at 18.52.42.png',
    '/Users/gferreira/Desktop/Screen Shot 2022-05-18 at 18.52.49.png',
    '/Users/gferreira/Desktop/Screen Shot 2022-05-18 at 18.52.54.png',
    '/Users/gferreira/Desktop/Screen Shot 2022-05-18 at 18.52.59.png',
    '/Users/gferreira/Desktop/Screen Shot 2022-05-18 at 18.53.04.png',
    # '/Users/gferreira/Desktop/Screen Shot 2022-05-18 at 18.53.08.png',
]

w, h = imageSize(imgs[0])

px, py = 21, 23

dx = (len(imgs)-1) * px
dy = (len(imgs)-1) * py

newPage(w+dx, h+dy)

translate(0, dy)

for img in imgs:
    w, h = imageSize(img)
    image(img, (0, 0))
    translate(px, -py)

# print(dx, dy)    
# image(imgTile, (-88, 468), alpha=0.5)

saveImage('/hipertipo/tools/tempEdit/docs/images/tempedit_mode-fonts.png')
