import cv2
import pickle

rect_width, rect_height = 107, 48

try:
    with open('parkingSlotPosition', 'rb') as f:
        posList = pickle.load(f)
except FileNotFoundError:
    posList = []


def mouseClick(events, x, y, flags, params):
    global posList
    # add car park position to the list
    if events == cv2.EVENT_LBUTTONDOWN:
        posList.append((x, y))

    # remove car park corresponding to mouse click
    if events == cv2.EVENT_MBUTTONDOWN:
        # finding the corresponding label to remove
        for index, pos in enumerate(posList):
            x1, y1 = pos
            # checking if the mouse click is within the label's range
            if x1 <= x <= x1 + rect_width and y1 <= y <= y1 + rect_height:
                posList.pop(index)

    # writing the label coordinates into the file
    with open('parkingSlotPosition', 'wb') as f:
        pickle.dump(posList, f)


while True:
    # refreshing the image
    img = cv2.imread('Dataset/carParkImg.png')
    for pos in posList:
        cv2.rectangle(img, pos, (pos[0] + rect_width, pos[1] + rect_height), (255, 255, 255), 2)
    cv2.imshow("Image", img)
    cv2.setMouseCallback("Image", mouseClick)
    if cv2.waitKey(1) == ord('q'):  # Exit when 'q' is pressed
        break

cv2.destroyAllWindows()
