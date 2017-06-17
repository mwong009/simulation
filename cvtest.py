import numpy as np
import cv2

def main():
    img = np.zeros((512,512,3), dtype=np.uint8)
    cv2.line(img, (0,0), (511,511), (255,0,0), 5)

    cv2.imshow('image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
