import cv2
import numpy
import random
import math
import time
import copy
from multiprocessing import Process, Queue, Array, Lock
import queue
from PIL import Image, ImageDraw, ImageFont, ImageFilter


#cd ~/Maze-Generator-in-Python/

##sudo apt update
##sudo apt install python3.12-venv
##python3.12 -m venv venv3.12

#source venv3.12/bin/activate

##pip install numpy
##pip install opencv-python
##pip install pillow
##pip install PyQt5
##pip install easydict
##sudo apt install python3.12-dev

#python3 ~/Maze-Generator-in-Python/MazeGenerator.py

#deactivate




does_quit = False # メイン ループの終了フラグ。

# ウィンドウの設定
window_name = "2D Maze"
cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_NORMAL)
cv2.moveWindow(window_name, 600, 200)






menu_window_number = 0

index_of_map_size = 5 # 指数。
map_array_width = 0
map_array_height = 0

upstairs = [0, 0] # 行、列。

window_width = 768
window_height = 768

shared_image_layer_1 = Array("f", window_width * window_height * 3)
shared_image_layer_2 = Array("f", window_width * window_height * 3)
shared_image_layer_2_alpha = Array("f", window_width * window_height * 3)
shared_image_layer_3 = Array("f", window_width * window_height * 3)
shared_image_layer_3_alpha = Array("f", window_width * window_height * 3)
shared_image_layer_4 = Array("f", window_width * window_height * 3)
shared_image_layer_4_alpha = Array("f", window_width * window_height * 3)
shared_image_layer_5 = Array("f", window_width * window_height * 3)
shared_image_layer_5_alpha = Array("f", window_width * window_height * 3)


#メニュー ウィンドウの矩形情報を格納する為のオブジェクトを作成する。
rectangle_of_menu_window = {
    "left": 4,
    "top": 4,
    "width": 180,
    "height": 40,
    "vertical_padding_of_menu": 5,
    "horizontal_padding_of_menu": 5,
    "width_of_menu": 0,
    "height_of_menu": 0,
    "rectangle_of_menu": []
}
rectangle_of_menu_window["width_of_menu"] = rectangle_of_menu_window["width"] - 2 * rectangle_of_menu_window["horizontal_padding_of_menu"]
rectangle_of_menu_window["height_of_menu"] = rectangle_of_menu_window["height"] - 2 * rectangle_of_menu_window["vertical_padding_of_menu"]



#メニュー項目の矩形情報を格納する為のオブジェクトを作成する。
rectangle_of_menu_window["rectangle_of_menu"].append({
    "text": "Generate New Maze",
    "left": rectangle_of_menu_window["left"] + 1 * rectangle_of_menu_window["horizontal_padding_of_menu"] + 0 * rectangle_of_menu_window["width_of_menu"],
    "top": rectangle_of_menu_window["top"] + 1 * rectangle_of_menu_window["vertical_padding_of_menu"] + 0 * rectangle_of_menu_window["height_of_menu"],
    "width": rectangle_of_menu_window["width_of_menu"],
    "height": rectangle_of_menu_window["height_of_menu"],
    "right": 0,
    "bottom": 0,
})
rectangle_of_menu_window["rectangle_of_menu"][0]["right"] = rectangle_of_menu_window["rectangle_of_menu"][0]["left"] + rectangle_of_menu_window["rectangle_of_menu"][0]["width"]
rectangle_of_menu_window["rectangle_of_menu"][0]["bottom"] = rectangle_of_menu_window["rectangle_of_menu"][0]["top"] + rectangle_of_menu_window["rectangle_of_menu"][0]["height"]

rectangle_of_menu_window["rectangle_of_menu"].append({
    "text": "Level Up",
    "left": rectangle_of_menu_window["left"] + 2 * rectangle_of_menu_window["horizontal_padding_of_menu"] + 1 * rectangle_of_menu_window["width_of_menu"],
    "top": rectangle_of_menu_window["top"] + 1 * rectangle_of_menu_window["vertical_padding_of_menu"] + 0 * rectangle_of_menu_window["height_of_menu"],
    "width": rectangle_of_menu_window["width_of_menu"],
    "height": rectangle_of_menu_window["height_of_menu"],
    "right": 0,
    "bottom": 0,
})
rectangle_of_menu_window["rectangle_of_menu"][1]["right"] = rectangle_of_menu_window["rectangle_of_menu"][1]["left"] + rectangle_of_menu_window["rectangle_of_menu"][1]["width"]
rectangle_of_menu_window["rectangle_of_menu"][1]["bottom"] = rectangle_of_menu_window["rectangle_of_menu"][1]["top"] + rectangle_of_menu_window["rectangle_of_menu"][1]["height"]

rectangle_of_menu_window["rectangle_of_menu"].append({
    "text": "Level Down",
    "left": rectangle_of_menu_window["left"] + 3 * rectangle_of_menu_window["horizontal_padding_of_menu"] + 2 * rectangle_of_menu_window["width_of_menu"],
    "top": rectangle_of_menu_window["top"] + 1 * rectangle_of_menu_window["vertical_padding_of_menu"] + 0 * rectangle_of_menu_window["height_of_menu"],
    "width": rectangle_of_menu_window["width_of_menu"],
    "height": rectangle_of_menu_window["height_of_menu"],
    "right": 0,
    "bottom": 0,
})
rectangle_of_menu_window["rectangle_of_menu"][2]["right"] = rectangle_of_menu_window["rectangle_of_menu"][2]["left"] + rectangle_of_menu_window["rectangle_of_menu"][2]["width"]
rectangle_of_menu_window["rectangle_of_menu"][2]["bottom"] = rectangle_of_menu_window["rectangle_of_menu"][2]["top"] + rectangle_of_menu_window["rectangle_of_menu"][2]["height"]


is_pointer_over_menu = Array("B", len(rectangle_of_menu_window["rectangle_of_menu"]))
is_menu_clicked = Array("B", len(rectangle_of_menu_window["rectangle_of_menu"]))




# 迷路表示領域の矩形情報を格納する為のオブジェクトを作成する。
rectangle_of_maze_map = {
    "left": 5,
    "top": 45,
    "width": window_width - 10,
    "height": window_height - 40 - 10,
    "right": window_width - 5,
    "bottom": window_height - 5
}






# ポインターの座標を格納する為の辞書を作成する。
pointer_coordinate = {
    "x": 0,
    "y": 0}






# 画面を初期化する為の関数を宣言する。
def initialize_image(lock, shared_map_array):
    image_layer_1 = numpy.frombuffer(shared_image_layer_1.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)
    image_layer_2 = numpy.frombuffer(shared_image_layer_2.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)
    image_layer_2_alpha = numpy.frombuffer(shared_image_layer_2_alpha.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)
    image_layer_3 = numpy.frombuffer(shared_image_layer_3.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)
    image_layer_3_alpha = numpy.frombuffer(shared_image_layer_3_alpha.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)
    image_layer_4 = numpy.frombuffer(shared_image_layer_4.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)
    image_layer_4_alpha = numpy.frombuffer(shared_image_layer_4_alpha.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)
    image_layer_5 = numpy.frombuffer(shared_image_layer_5.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)
    image_layer_5_alpha = numpy.frombuffer(shared_image_layer_5_alpha.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)

    # 迷路表示領域の矩形情報を格納する為のオブジェクトの大きさを初期化する。
    rectangle_of_maze_map["width"] = window_width - 10
    rectangle_of_maze_map["height"] = window_height - 40 - 10
    rectangle_of_maze_map["right"] = window_width - 5
    rectangle_of_maze_map["bottom"] = window_height - 5

    #オフスクリーン描画用のimage要素のコンテキストを作成する。
    # アルファ チャンネルの処理の為、浮動小数点数型にする。
    image_layer_1.fill(0.)
    image_layer_2.fill(0.)
    image_layer_2_alpha.fill(0.)
    image_layer_3.fill(0.)
    image_layer_3_alpha.fill(0.)
    image_layer_4.fill(0.)
    image_layer_4_alpha.fill(0.)
    image_layer_5.fill(0.)
    image_layer_5_alpha.fill(0.)

    # image レイヤーを初期化する。
    clear_image_layer()


    


# image レイヤーを初期化する為の関数を宣言する。
def clear_image_layer():
    image_layer_1 = numpy.frombuffer(shared_image_layer_1.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)
    image_layer_2 = numpy.frombuffer(shared_image_layer_2.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)
    image_layer_2_alpha = numpy.frombuffer(shared_image_layer_2_alpha.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)
    image_layer_3 = numpy.frombuffer(shared_image_layer_3.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)
    image_layer_3_alpha = numpy.frombuffer(shared_image_layer_3_alpha.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)
    image_layer_4 = numpy.frombuffer(shared_image_layer_4.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)
    image_layer_4_alpha = numpy.frombuffer(shared_image_layer_4_alpha.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)
    image_layer_5 = numpy.frombuffer(shared_image_layer_5.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)
    image_layer_5_alpha = numpy.frombuffer(shared_image_layer_5_alpha.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)

    image_layer_1.fill(0.)
    image_layer_2.fill(0.)
    image_layer_2_alpha.fill(0.)
    image_layer_3.fill(0.)
    image_layer_3_alpha.fill(0.)
    image_layer_4.fill(0.)
    image_layer_4_alpha.fill(0.)
    image_layer_5.fill(0.)
    image_layer_5_alpha.fill(0.)

    # 背景のimageレイヤーに対して塗り潰しを行う。
    image_layer_1.fill(0.2)





has_clicked_or_touched = False
clicked_x = 0
clicked_y = 0

def trace_pointer(event, x, y, flags, params):
    global pointer_coordinate
    global has_clicked_or_touched
    global clicked_x
    global clicked_y

    lock = params

    image_layer_5 = numpy.frombuffer(shared_image_layer_5.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)
    image_layer_5_alpha = numpy.frombuffer(shared_image_layer_5_alpha.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)

    pointer_coordinate["x"] = x
    pointer_coordinate["y"] = y

    # ポインターの円を描画する。
    image_layer_5.fill(0.)
    image_layer_5_alpha.fill(0.)
    cv2.circle(image_layer_5, (x, y), 6, (1., 1., 1.), thickness=-1, lineType=cv2.LINE_AA)
    cv2.circle(image_layer_5_alpha, (x, y), 6, (1., 1., 1.), thickness=-1, lineType=cv2.LINE_AA)

    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_x = x
        clicked_y = y
        has_clicked_or_touched = True
        print('Clicked: clicked_x: {} clicked_y: {}'.format(clicked_x, clicked_y))







# 規定の時間経過後に関数を実行する関数を定義する。
def set_timeout(target_function, arguments, wait_time):
    time.sleep(wait_time)
    target_function(arguments)






def put_text(image, image_alpha, text, point, size, color):
    # HWC BGR [0., 1.] color(R, G, B) [0., 1.]
    color = tuple(map(lambda x: x * 255, color))
    color = tuple(map(round, color))
    font = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", size)

    image = (cv2.cvtColor(image, cv2.COLOR_BGR2RGB) * 255).astype(numpy.uint8) # HWC RGB [0, 255]
    pillow_image = Image.fromarray(image) # WHC RGB [0, 255]
    pillow_image = pillow_image.convert("RGBA") # WHC RGBA [0, 255]

    blured_text_image = Image.new("RGBA", pillow_image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(blured_text_image)
    draw.text(point, text, fill=(0, 0, 0, 255), font=font) # Draw the outline of the text.
    blured_text_image = blured_text_image.filter(ImageFilter.GaussianBlur(radius=math.sqrt(math.sqrt(size))))
    combined_image = Image.alpha_composite(pillow_image, blured_text_image)
    draw = ImageDraw.Draw(combined_image)
    draw.text(point, text, fill=color, font=font) # Draw the text on top of the blurred image.
    combined_image = numpy.array(combined_image) #  HWC RGBA [0, 255]

    result_image = numpy.zeros((pillow_image.height, pillow_image.width, 3)) # HWC RGB [0, 255]
    result_image[:, :, 0] = combined_image[:, :, 0]
    result_image[:, :, 1] = combined_image[:, :, 1]
    result_image[:, :, 2] = combined_image[:, :, 2]
    result_image = (result_image / 255).astype(numpy.float32)
    result_image = cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR) # cv2.cvtColor() doesn't support CV_64F.


    image_alpha = (cv2.cvtColor(image_alpha, cv2.COLOR_BGR2RGB) * 255).astype(numpy.uint8) # HWC RGB [0, 255]
    pillow_image_alpha = Image.fromarray(image_alpha) # WHC RGB [0, 255]
    pillow_image_alpha = pillow_image_alpha.convert("RGBA") # WHC RGBA [0, 255]

    blured_text_image_alpha = Image.new("RGBA", pillow_image_alpha.size, (0, 0, 0, 0))
    draw_alpha = ImageDraw.Draw(blured_text_image_alpha)
    draw_alpha.text(point, text, fill=(255, 255, 255, 255), font=font) # Draw the outline of the text.
    blured_text_image_alpha = blured_text_image_alpha.filter(ImageFilter.GaussianBlur(radius=math.sqrt(math.sqrt(size))))
    combined_image_alpha = Image.alpha_composite(pillow_image_alpha, blured_text_image_alpha)
    draw_alpha = ImageDraw.Draw(combined_image_alpha)
    draw_alpha.text(point, text, fill=(255, 255, 255, 255), font=font) # Draw the text on top of the blurred image.
    combined_image_alpha = numpy.array(combined_image_alpha) #  HWC RGBA [0, 255]

    result_image_alpha = numpy.zeros((pillow_image_alpha.height, pillow_image_alpha.width, 3)) # HWC RGB [0, 255]
    result_image_alpha[:, :, 0] = combined_image_alpha[:, :, 0]
    result_image_alpha[:, :, 1] = combined_image_alpha[:, :, 1]
    result_image_alpha[:, :, 2] = combined_image_alpha[:, :, 2]
    result_image_alpha = (result_image_alpha / 255).astype(numpy.float32)
    result_image_alpha = cv2.cvtColor(result_image_alpha, cv2.COLOR_RGB2BGR) # cv2.cvtColor() doesn't support CV_64F.


    return result_image, result_image_alpha







# 壁延ばし法による迷路生成処理を実行する為の関数を宣言する。
def generate_maze(lock, shared_map_array, shared_downstairs, shared_current_position):
    global map_array_width
    global map_array_height

    map_array = numpy.frombuffer(shared_map_array.get_obj(), dtype=numpy.uint8).reshape(map_array_width, map_array_height)

    # 外枠境界の処理の為に地図の2次元配列の辺縁を厚みが3枡分のTrue(壁)で埋める。
    print(f"map_array_width: {map_array_width}")
    for i in range(map_array_width):
        map_array[0][i] = True
        map_array[1][i] = True
        map_array[2][i] = True
        map_array[map_array_height - 3][i] = True
        map_array[map_array_height - 2][i] = True
        map_array[map_array_height - 1][i] = True

    print(f"map_array_height: {map_array_height}")
    for i in range(2, map_array_height - 2):
        map_array[i][0] = True
        map_array[i][1] = True
        map_array[i][2] = True
        map_array[i][map_array_width - 3] = True
        map_array[i][map_array_width - 2] = True
        map_array[i][map_array_width - 1] = True

    # 壁延ばし法により迷路を生成する。

    map_queue = [] # 行、列の2要素の1次元配列のキュー。
    for i in range(2, map_array_height - 2, 2):
        for j in range(2, map_array_width - 2, 2):
            # 壁かつ探索可能な枡目を記録する。
            if map_array[i][j] == True:
                map_queue.append([i, j])


    loop_flag = True
    loop_counter = 0
    max_loop_count = 4 ** index_of_map_size * 0.1
    random_number = 0
    k = 0 # 上下左右の何れかを示す。
    l = 0
    while len(map_queue) > 0 and loop_counter < max_loop_count:
    # 始点を置く。
        random_number = math.floor(random.random() * len(map_queue))
        i = map_queue[random_number][0]
        j = map_queue[random_number][1]
        del map_queue[random_number:1] # 探索済みの座標を削除する。

        loop_flag = True
        while loop_flag == True:
            if map_array[i][j] == True and (map_array[i - 2][j] == False or map_array[i][j - 2] == False or map_array[i][j + 2] == False or map_array[i + 2][j] == False):
            # その枡目が壁であり、かつ上下左右の内いずれかの方向の2枡先が空間ならば以下の処理を実行する。

                map_queue.append([i, j]) # 壁にした座標をキューに追加する。

                k = math.floor(random.random() * 4)
                if k == 0 and map_array[i - 2][j] == False:
                    map_array[i - 1][j] = True
                    map_array[i - 2][j] = True
                    i -= 2
                elif k == 1 and map_array[i][j - 2] == False:
                    map_array[i][j - 1] = True
                    map_array[i][j - 2] = True
                    j -= 2
                elif k == 2 and map_array[i][j + 2] == False:
                    map_array[i][j + 1] = True
                    map_array[i][j + 2] = True
                    j += 2
                elif k == 3 and map_array[i + 2][j] == False:
                    map_array[i + 1][j] = True
                    map_array[i + 2][j] = True
                    i += 2
            else:
                loop_flag = False
        loop_counter += 1

    print(map_array)

    # 階段を設置する。
    place_stair(lock, shared_map_array, shared_downstairs, shared_current_position)





# 迷路に階段を配置する為の関数を宣言する。
def place_stair(lock, shared_map_array, shared_downstairs, shared_current_position):
    global map_array_width
    global map_array_height
    global upstairs

    map_array = numpy.frombuffer(shared_map_array.get_obj(), dtype=numpy.uint8).reshape(map_array_width, map_array_height)
    downstairs = numpy.frombuffer(shared_downstairs.get_obj(), dtype=numpy.uint16)
    current_position = numpy.frombuffer(shared_current_position.get_obj(), dtype=numpy.uint16)

    i = 0
    j = 0
    k = 0
    l = 0

    # 幅優先探索により最も遠い2点を選ぶ。

    # ランダムに探索開始地点を選ぶ。
    vertex = [0, 0]
    while True:
        i = math.floor(random.random() * ((map_array_height - 5) / 2) ) * 2 + 3
        j = math.floor(random.random() * ((map_array_height - 5) / 2) ) * 2 + 3
        if map_array[i][j] == False:
        # その枡目が空間であるならば以下の処理を実行する。
            vertex[0] = i
            vertex[1] = j
            break # ループを止める。

    # 最も遠い地点を求める為の関数を宣言する。
    def serch_farthest(map_array, vertex):
        search_array = copy.deepcopy(map_array) # 配列をディープ コピーする。
        vertex_child = [0, 0]
        queue = Queue() # FIFO のキューを作成する。

        # キューの配列の末尾に要素を追加する。
        queue.put(copy.deepcopy(vertex))

        while queue.qsize() != 0:

            # キューの先頭の要素を取得してから除去する。
            vertex = queue.get()

            if search_array[vertex[0]][vertex[1]] == False:

                if search_array[vertex[0] + 1][vertex[1]] == False:

                    # その地点の座標を子頂点として記録する。
                    vertex_child = copy.deepcopy(vertex)

                    # その方向に進行可能ならばキューの最後に次の座標を追加する。
                    vertex_child[0] += 1
                    queue.put(copy.deepcopy(vertex_child))

                if search_array[vertex[0]][vertex[1] + 1] == False:

                    # その地点の座標を子頂点として記録する。
                    vertex_child = copy.deepcopy(vertex)

                    # その方向に進行可能ならばキューの最後に次の座標を追加する。
                    vertex_child[1] += 1
                    queue.put(copy.deepcopy(vertex_child))

                if search_array[vertex[0] - 1][vertex[1]] == False:

                    # その地点の座標を子頂点として記録する。
                    vertex_child = copy.deepcopy(vertex)

                    # その方向に進行可能ならばキューの最後に次の座標を追加する。
                    vertex_child[0] -= 1
                    queue.put(copy.deepcopy(vertex_child))

                if search_array[vertex[0]][vertex[1] - 1] == False:

                    # その地点の座標を子頂点として記録する。
                    vertex_child = copy.deepcopy(vertex)

                    # その方向に進行可能ならばキューの最後に次の座標を追加する。
                    vertex_child[1] -= 1
                    queue.put(copy.deepcopy(vertex_child))

                # 探索済みの地点を埋める。
                search_array[vertex[0]][vertex[1]] = True

        return search_array, vertex

    # ランダムに選んだ出発地点から最も遠い地点を求める。
    search_array, vertex = serch_farthest(map_array, vertex)

    # 出発地点を更新する。
    upstairs[0] = vertex[0]
    upstairs[1] = vertex[1]

    # 現在位置を階段上にする。
    current_position[0] = upstairs[0]
    current_position[1] = upstairs[1]

    # 更新した出発地点から最も遠い地点を求める。
    search_array, vertex = serch_farthest(map_array, vertex)

    # 終着地点。
    downstairs[0] = vertex[0]
    downstairs[1] = vertex[1]

    # 迷路を描画する。
    draw_maze(lock, shared_map_array, shared_downstairs, shared_current_position)






# 迷路を描画する為の関数を宣言する。
def draw_maze(lock, shared_map_array, shared_downstairs, shared_current_position):
    global map_array_width
    global map_array_height
    global upstairs

    # BGR [0., 1.]

    # OpenCV でサブピクセル座標で描画する為に座標値をスケーリングする。
    shift = 8 # ビット シフト値 (2^8 = 256)
    scale_factor = 2 ** shift

    map_array = numpy.frombuffer(shared_map_array.get_obj(), dtype=numpy.uint8).reshape(map_array_width, map_array_height)
    downstairs = numpy.frombuffer(shared_downstairs.get_obj(), dtype=numpy.uint16)

    image_layer_3 = numpy.frombuffer(shared_image_layer_3.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)
    image_layer_3_alpha = numpy.frombuffer(shared_image_layer_3_alpha.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)

    image_layer_3_uint8 = (image_layer_3 * 255).astype(numpy.uint8)
    image_layer_3_alpha_uint8 = (image_layer_3_alpha * 255).astype(numpy.uint8)

    # 元の描画用レイヤーの内容を消去する。
    image_layer_3_uint8.fill(0)
    image_layer_3_alpha_uint8.fill(0)

    # 迷路表示領域を描画する。
    point_1 = (rectangle_of_maze_map["left"], rectangle_of_maze_map["top"])
    point_2 = (point_1[0] + rectangle_of_maze_map["width"], point_1[1] + rectangle_of_maze_map["height"])
    cv2.rectangle(image_layer_3_uint8, point_1, point_2, (224, 224, 224), thickness=-1, lineType=cv2.LINE_AA, shift=0)
    cv2.rectangle(image_layer_3_alpha_uint8, point_1, point_2, (255, 255, 255), thickness=-1, lineType=cv2.LINE_AA, shift=0)


    # 地図の2次元配列に基づいて迷路を描画する。

    grid_width = rectangle_of_maze_map["width"] / (map_array_width - 3 - 1.3)
    grid_height = rectangle_of_maze_map["height"] / (map_array_height - 3 - 1.3)
    for i in range(map_array_height - 4):
        for j in range(map_array_width - 4):
            point_1 = (int((rectangle_of_maze_map["left"] + math.ceil(j / 2) * grid_width * 0.7 + math.floor(j / 2) * grid_width * 1.3) * scale_factor), 
                int((rectangle_of_maze_map["top"] + math.ceil(i / 2) * grid_height * 0.7 + math.floor(i / 2) * grid_height * 1.3) * scale_factor))

            if i % 2 == 1 and  j % 2 == 1:
            # 奇数行かつ奇数列ならば以下の処理を行う。
                color = (208, 208, 208)
                alpha = (255, 255, 255)
                point_2 = (int(point_1[0] + grid_width * 1.3 * scale_factor), int(point_1[1] + grid_height * 1.3 * scale_factor))
                cv2.rectangle(image_layer_3_uint8, point_1, point_2, color, thickness=-1, lineType=cv2.LINE_AA, shift=shift)
                cv2.rectangle(image_layer_3_alpha_uint8, point_1, point_2, alpha, thickness=-1, lineType=cv2.LINE_AA, shift=shift)

            elif i % 2 == 1 and  j % 2 == 0:
            # 奇数行かつ偶数列ならば以下の処理を行う。
                if map_array[i + 2][j + 2] == False:
                    color = (192, 192, 192)
                    alpha = (255, 255, 255)
                else:
                    color = (24, 24, 24)
                    alpha = (255, 255, 255)

                point_2 = (int(point_1[0] + grid_width * 0.7 * scale_factor), int(point_1[1] + grid_height * 1.3 * scale_factor))
                cv2.rectangle(image_layer_3_uint8, point_1, point_2, color, thickness=-1, lineType=cv2.LINE_AA, shift=shift)
                cv2.rectangle(image_layer_3_alpha_uint8, point_1, point_2, alpha, thickness=-1, lineType=cv2.LINE_AA, shift=shift)

            elif i % 2 == 0 and  j % 2 == 1:
            # 偶数行かつ奇数列ならば以下の処理を行う。
                if map_array[i + 2][j + 2] == False:
                    color = (192, 192, 192)
                    alpha = (255, 255, 255)
                else:
                    color = (24, 24, 24)
                    alpha = (255, 255, 255)

                point_2 = (int(point_1[0] + grid_width * 1.3 * scale_factor), int(point_1[1] + grid_height * 0.7 * scale_factor))
                cv2.rectangle(image_layer_3_uint8, point_1, point_2, color, thickness=-1, lineType=cv2.LINE_AA, shift=shift)
                cv2.rectangle(image_layer_3_alpha_uint8, point_1, point_2, alpha, thickness=-1, lineType=cv2.LINE_AA, shift=shift)

            elif i % 2 == 0 and  j % 2 == 0:
            # 偶数行かつ偶数列ならば以下の処理を行う。
                if map_array[i + 2][j + 2] == False:
                    color = (192, 192, 192)
                    alpha = (255, 255, 255)
                else:
                    color = (24, 24, 24)
                    alpha = (255, 255, 255)

                point_2 = (int(point_1[0] + grid_width * 0.7 * scale_factor), int(point_1[1] + grid_height * 0.7 * scale_factor))
                cv2.rectangle(image_layer_3_uint8, point_1, point_2, color, thickness=-1, lineType=cv2.LINE_AA, shift=shift)
                cv2.rectangle(image_layer_3_alpha_uint8, point_1, point_2, alpha, thickness=-1, lineType=cv2.LINE_AA, shift=shift)

            # 開始地点を表す赤色の枡目を描画する。
            if i + 2 == upstairs[0] and j + 2 == upstairs[1]:
                color = (16, 16, 128)
                alpha = (255, 255, 255)
                point_2 = (int(point_1[0] + grid_width * 1.3 * scale_factor), int(point_1[1] + grid_height * 1.3 * scale_factor))
                cv2.rectangle(image_layer_3_uint8, point_1, point_2, color, thickness=-1, lineType=cv2.LINE_AA, shift=shift)
                cv2.rectangle(image_layer_3_alpha_uint8, point_1, point_2, alpha, thickness=-1, lineType=cv2.LINE_AA, shift=shift)

            # 終着地点を表す緑色の枡目を描画する。
            if i + 2 == downstairs[0] and j + 2 == downstairs[1]:
                color = (12, 96, 12)
                alpha = (255, 255, 255)
                point_2 = (int(point_1[0] + grid_width * 1.3 * scale_factor), int(point_1[1] + grid_height * 1.3 * scale_factor))
                cv2.rectangle(image_layer_3_uint8, point_1, point_2, color, thickness=-1, lineType=cv2.LINE_AA, shift=shift)
                cv2.rectangle(image_layer_3_alpha_uint8, point_1, point_2, alpha, thickness=-1, lineType=cv2.LINE_AA, shift=shift)

    image_layer_3[:, :, :] = image_layer_3_uint8[:, :, :] / 255.
    image_layer_3_alpha[:, :, :] = image_layer_3_alpha_uint8[:, :, :] / 255.

    # 駒を描画する。
    with lock:
        draw_position(shared_map_array, shared_downstairs, shared_current_position)



# 駒を描画する為の関数を宣言する。
def draw_position(shared_map_array, shared_downstairs, shared_current_position):
    global map_array_width
    global map_array_height

    downstairs = numpy.frombuffer(shared_downstairs.get_obj(), dtype=numpy.uint16)
    current_position = numpy.frombuffer(shared_current_position.get_obj(), dtype=numpy.uint16)

    # BGR [0., 1.]

    # OpenCV でサブピクセル座標で描画する為に座標値をスケーリングする。
    shift = 8 # ビット シフト値 (2^8 = 256)
    scale_factor = 2 ** shift

    map_array = numpy.frombuffer(shared_map_array.get_obj(), dtype=numpy.uint8).reshape(map_array_width, map_array_height)

    image_layer_4 = numpy.frombuffer(shared_image_layer_4.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)
    image_layer_4_alpha = numpy.frombuffer(shared_image_layer_4_alpha.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)

    image_layer_4_uint8 = (image_layer_4 * 255).astype(numpy.uint8)
    image_layer_4_alpha_uint8 = (image_layer_4_alpha * 255).astype(numpy.uint8)

    # 元の描画用レイヤーの内容を消去する。
    image_layer_4_uint8.fill(0)
    image_layer_4_alpha_uint8.fill(0)


    # 駒を描画する。

    grid_width = rectangle_of_maze_map["width"] / (map_array_width - 3 - 1.3)
    grid_height = rectangle_of_maze_map["height"] / (map_array_height - 3 - 1.3)
    color = (192, 16, 16)
    alpha = (255, 255, 255)
    point_1 = (int((rectangle_of_maze_map["left"] + math.ceil((current_position[1] - 2) / 2) * grid_width * 0.7 + math.floor((current_position[1] - 2) / 2) * grid_width * 1.3) * scale_factor), 
        int((rectangle_of_maze_map["top"] + math.ceil((current_position[0] - 2) / 2) * grid_height * 0.7 + math.floor((current_position[0] - 2) / 2) * grid_height * 1.3) * scale_factor))
    point_2 = (int(point_1[0] + grid_width * 1.3 * scale_factor), int(point_1[1] + grid_height * 1.3 * scale_factor))
    cv2.rectangle(image_layer_4_uint8, point_1, point_2, color, thickness=-1, lineType=cv2.LINE_AA, shift=shift)
    cv2.rectangle(image_layer_4_alpha_uint8, point_1, point_2, alpha, thickness=-1, lineType=cv2.LINE_AA, shift=shift)

    image_layer_4[:, :, :] = image_layer_4_uint8[:, :, :] / 255.
    image_layer_4_alpha[:, :, :] = image_layer_4_alpha_uint8[:, :, :] / 255.

    print(f"downstairs x: {downstairs[1]}, y: {downstairs[0]}")
    print(f"current_position x: {current_position[1]}, y: {current_position[0]}")

    # 駒が終着地点にあったら文字列を表示する。
    if downstairs[0] == current_position[0] and downstairs[1] == current_position[1]:

        text = "You solved !!"
        coordinate = (rectangle_of_maze_map["left"] + rectangle_of_maze_map["width"] / 8, rectangle_of_maze_map["top"] + rectangle_of_maze_map["height"] / 2)
        drawn_image, drawn_image_alpha = put_text(image_layer_4, image_layer_4_alpha, text, coordinate, 96, (0.25, 0.5, 0.75))
        numpy.copyto(image_layer_4, drawn_image)
        numpy.copyto(image_layer_4_alpha, drawn_image_alpha)
        print("You solved.")






# メニュー ウィンドウを描画する為の関数を宣言する。
def draw_menu(lock):
    with lock:
        image_layer_2 = numpy.frombuffer(shared_image_layer_2.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)
        image_layer_2_alpha = numpy.frombuffer(shared_image_layer_2_alpha.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)

        image_layer_2.fill(0.)
        image_layer_2_alpha.fill(0.)

        # メニューを描画する。
        for menu_rectangle_number in range(len(rectangle_of_menu_window["rectangle_of_menu"])):

            if is_menu_clicked[menu_rectangle_number] == True:
            # もしそのメニュー項目の上でポインターが押された直後ならば以下の処理を行う。
                print("Menu is clicked.")

                # メニュー項目のボタンを描画する。
                point_1 = (rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["left"], rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["top"])
                point_2 = (point_1[0] + rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["width"], point_1[1] + rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["height"])
                cv2.rectangle(image_layer_2, point_1, point_2, (0.2, 0.2, 0.2), thickness=-1, lineType=cv2.LINE_AA, shift=0)
                cv2.rectangle(image_layer_2, point_1, point_2, (0.75, 0.75, 0.75), thickness=2, lineType=cv2.LINE_AA, shift=0)
                cv2.rectangle(image_layer_2_alpha, point_1, point_2, (1., 1., 1.), thickness=-1, lineType=cv2.LINE_AA, shift=0)

                ## 文字列を描画する。
                text = rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["text"]
                coordinate = (rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["left"] + 8, rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["top"] + 4)
                drawn_image, _ = put_text(image_layer_2, image_layer_2_alpha, text, coordinate, 16, (0.5, 0.5, 0.5))
                numpy.copyto(image_layer_2, drawn_image)

                print("Text was drawn.")

            elif is_pointer_over_menu[menu_rectangle_number] == True:
            # もしそのメニュー項目の上でポインターが押された直後ではなく、かつポインターがそのメニュー項目の上に有ったならば以下の処理を行う。

                print("Pointer is over the menu.")

                # メニュー項目のボタンを描画する。
                point_1 = (rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["left"], rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["top"])
                point_2 = (point_1[0] + rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["width"], point_1[1] + rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["height"])
                cv2.rectangle(image_layer_2, point_1, point_2, (0.5, 0.5, 0.5), thickness=-1, lineType=cv2.LINE_AA, shift=0)
                cv2.rectangle(image_layer_2, point_1, point_2, (0.95, 0.95, 0.95), thickness=2, lineType=cv2.LINE_AA, shift=0)
                cv2.rectangle(image_layer_2_alpha, point_1, point_2, (1., 1., 1.), thickness=-1, lineType=cv2.LINE_AA, shift=0)

                ## 文字列を描画する。
                text = rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["text"]
                coordinate = (rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["left"] + 8, rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["top"] + 4)
                drawn_image, _ = put_text(image_layer_2, image_layer_2_alpha, text, coordinate, 16, (1.0, 1.0, 1.0))
                numpy.copyto(image_layer_2, drawn_image)

            else:
            # もしそのメニュー項目の上でポインターが押された直後ではなく、かつポインターがそのメニュー項目の上に無いならば以下の処理を行う。

                print("Pointer is not over the menu.")

                # メニュー項目のボタンを描画する。
                point_1 = (rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["left"], rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["top"])
                point_2 = (point_1[0] + rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["width"], point_1[1] + rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["height"])
                cv2.rectangle(image_layer_2, point_1, point_2, (0.25, 0.25, 0.25), thickness=-1, lineType=cv2.LINE_AA, shift=0)
                cv2.rectangle(image_layer_2, point_1, point_2, (0.95, 0.95, 0.95), thickness=2, lineType=cv2.LINE_AA, shift=0)
                cv2.rectangle(image_layer_2_alpha, point_1, point_2, (1., 1., 1.), thickness=-1, lineType=cv2.LINE_AA, shift=0)

                ## 文字列を描画する。
                text = rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["text"]
                coordinate = (rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["left"] + 8, rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["top"] + 4)
                drawn_image, _ = put_text(image_layer_2, image_layer_2_alpha, text, coordinate, 16, (1.0, 1.0, 1.0))
                numpy.copyto(image_layer_2, drawn_image)


        x = int(rectangle_of_menu_window["rectangle_of_menu"][len(rectangle_of_menu_window["rectangle_of_menu"]) - 1]["right"] + rectangle_of_menu_window["rectangle_of_menu"][len(rectangle_of_menu_window["rectangle_of_menu"]) - 1]["width"] / 8)
        y = int(rectangle_of_menu_window["rectangle_of_menu"][len(rectangle_of_menu_window["rectangle_of_menu"]) - 1]["top"])
        coordinate = (x, y)
        text = "Lv: " + str(index_of_map_size - 2)
        drawn_image, drawn_image_alpha = put_text(image_layer_2, image_layer_2_alpha, text, coordinate, 20, (1.0, 1.0, 1.0))
        numpy.copyto(image_layer_2, drawn_image)
        numpy.copyto(image_layer_2_alpha, drawn_image_alpha)






def click_effect_timeout(arguments):
    print("Timeout.")
    menu_rectangle_number, lock = arguments
    is_menu_clicked[menu_rectangle_number] = False
    draw_menu(lock)






# 初期化する為の関数を宣言する。
def initialize(lock):
    global map_array_width
    global map_array_height

    #イヴェント リスナーを解除する。
    #removeAllOfInteractiveCanvasListener();

    # 迷路のサイズ用の変数を初期化する。
    map_array_width = 2 ** index_of_map_size + 1 + 4
    map_array_height = 2 ** index_of_map_size + 1 + 4

    # マルチプロセッシングの為に迷路の2次元共有配列を確保する。
    shared_map_array = Array("B", map_array_width * map_array_height) # 行、列の2次元配列。
    map_array = numpy.frombuffer(shared_map_array.get_obj(), dtype=numpy.uint8).reshape(map_array_width, map_array_height)

    # 迷路の2次元配列をFalse(空間)で埋めて初期化する。
    map_array = [[False] * map_array_width for i in range(map_array_height)]

    shared_downstairs = Array("I", 2) # マルチプロセッシングの為に終着地点の行、列を表す2要素の1次元共有配列を確保する。

    # 現在位置を初期化する。
    shared_current_position = Array("I", 2) # マルチプロセッシングの為に迷路上での現在位置の行、列を表す2要素の1次元共有配列を確保する。
    current_position = numpy.frombuffer(shared_current_position.get_obj(), dtype=numpy.uint16)
    current_position[0] = 0
    current_position[1] = 0

    # 画像を初期化する。
    initialize_image(lock, shared_map_array)

    # メニューを描画する。
    draw_menu(lock)

    # 子プロセスで迷路を生成する関数を実行させる。
    process_for_maze_generation = Process(target=generate_maze, args=(lock, shared_map_array, shared_downstairs, shared_current_position))
    process_for_maze_generation.start()
    print(f"current_position: {current_position}")

    '''
    current_position を shared array に変更する。
    '''

    return shared_map_array, shared_downstairs, shared_current_position





# マウス ボタンを押した際の処理を行う関数を宣言する。
def process_click(lock):
    global index_of_map_size
    for menu_rectangle_number in range(len(rectangle_of_menu_window["rectangle_of_menu"])):
        if is_menu_clicked[menu_rectangle_number] == True:
        # もしポインターがそのメニュー項目の上でクリックされたならば以下の処理を行う。

            if menu_rectangle_number == 0:
                # 初期化する。
                print("initialize")

            if menu_rectangle_number == 1:
                #レヴェルを上げる。
                if index_of_map_size < 9:
                    index_of_map_size += 1
                print("Level Up")

            if menu_rectangle_number == 2:
                #レヴェルを下げる。
                if index_of_map_size > 2:
                    index_of_map_size -= 1
                print("Level Down")

            shared_map_array, shared_downstairs, shared_current_position = initialize(lock)

            # タイムアウト関数により、一定時間後に画面を更新する関数を実行させる。
            draw_menu(lock)
            set_timeout_process = Process(target=set_timeout, args=(click_effect_timeout, (menu_rectangle_number, lock), 0.2))
            set_timeout_process.start()
            break

    return shared_map_array, shared_downstairs, shared_current_position





# 画面を表示する為の関数を宣言する。
def display_image(lock):
    # BGR [0., 1.]
    with lock:
        image_layer_1 = numpy.frombuffer(shared_image_layer_1.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)
        image_layer_2 = numpy.frombuffer(shared_image_layer_2.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)
        image_layer_2_alpha = numpy.frombuffer(shared_image_layer_2_alpha.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)
        image_layer_3 = numpy.frombuffer(shared_image_layer_3.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)
        image_layer_3_alpha = numpy.frombuffer(shared_image_layer_3_alpha.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)
        image_layer_4 = numpy.frombuffer(shared_image_layer_4.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)
        image_layer_4_alpha = numpy.frombuffer(shared_image_layer_4_alpha.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)
        image_layer_5 = numpy.frombuffer(shared_image_layer_5.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)
        image_layer_5_alpha = numpy.frombuffer(shared_image_layer_5_alpha.get_obj(), dtype=numpy.float32).reshape(window_height, window_width, 3)

        # 実際に画面上に表示されるimage要素のコンテキストに対してオフスクリーン描画用のimage要素の内容を転写する。
        image = image_layer_1.copy() # 背景を複製する。
        image = (1. - image_layer_2_alpha) * image + image_layer_2_alpha * image_layer_2 # メニュー ウィンドウの画像を合成する。
        image = (1. - image_layer_3_alpha) * image + image_layer_3_alpha * image_layer_3 # 迷路の画像を合成する。
        image = (1. - image_layer_4_alpha) * image + image_layer_4_alpha * image_layer_4 # 駒の画像を合成する。
        image = (1. - image_layer_5_alpha) * image + image_layer_5_alpha * image_layer_5 # ポインターの画像を合成する。

        cv2.imshow(window_name, image) # ウィンドウに画像を表示する。






if __name__ == "__main__":
    lock = Lock()
    shared_map_array, shared_downstairs, shared_current_position = initialize(lock)
    map_array = numpy.frombuffer(shared_map_array.get_obj(), dtype=numpy.uint8).reshape(map_array_width, map_array_height)
    current_position = numpy.frombuffer(shared_current_position.get_obj(), dtype=numpy.uint16)
    cv2.setMouseCallback(window_name, trace_pointer, lock)

    while True:
        display_image(lock)

        for menu_rectangle_number in range(len(rectangle_of_menu_window["rectangle_of_menu"])):
            if pointer_coordinate["x"] >= rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["left"] and \
                pointer_coordinate["x"] < rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["right"] and \
                pointer_coordinate["y"] >= rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["top"] and \
                pointer_coordinate["y"] < rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["bottom"]:
            # もしポインターがそのメニュー項目の上に有るならば以下の処理を行う。

                if is_pointer_over_menu[menu_rectangle_number] == False:
                    is_pointer_over_menu[menu_rectangle_number] = True
                    print()
                    print(f"Pointer is over the menu: {menu_rectangle_number}")
                    print()
                    draw_menu(lock)
            else:
                if is_pointer_over_menu[menu_rectangle_number] == True:
                    print()
                    print(f"Pointer is off the menu: {menu_rectangle_number}")
                    print()
                    is_pointer_over_menu[menu_rectangle_number] = False
                    draw_menu(lock)


        if has_clicked_or_touched == True:
            has_clicked_or_touched = False
            for menu_rectangle_number in range(len(rectangle_of_menu_window["rectangle_of_menu"])):
                if pointer_coordinate["x"] >= rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["left"] and \
                    pointer_coordinate["x"] < rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["right"] and \
                    pointer_coordinate["y"] >= rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["top"] and \
                    pointer_coordinate["y"] < rectangle_of_menu_window["rectangle_of_menu"][menu_rectangle_number]["bottom"]:
                # もしポインターがそのメニュー項目の上に有るならば以下の処理を行う。

                    is_menu_clicked[menu_rectangle_number] = True

                    # メニュー クリック時の処理を行う。
                    shared_map_array, shared_downstairs, shared_current_position = process_click(lock)
                    map_array = numpy.frombuffer(shared_map_array.get_obj(), dtype=numpy.uint8).reshape(map_array_width, map_array_height)
                    current_position = numpy.frombuffer(shared_current_position.get_obj(), dtype=numpy.uint16)
                    break




        pressed_key = cv2.waitKey(10) & 0xFF
        if pressed_key == ord("q"):
            # 終了する。
            break

        elif pressed_key == ord("s") or pressed_key == ord("j"):
            print("Pressed key: s or j")
            # 現在位置を左へ移動させる。
            if map_array[current_position[0]][current_position[1] - 1] == False:
                current_position[1] -= 2
                draw_position(shared_map_array, shared_downstairs, shared_current_position)

        elif pressed_key == ord("e") or pressed_key == ord("i"):
            print("Pressed key: e or i")
            # 現在位置を上へ移動させる。
            if map_array[current_position[0] - 1][current_position[1]] == False:
                current_position[0] -= 2;
                draw_position(shared_map_array, shared_downstairs, shared_current_position)

        elif pressed_key == ord("f") or pressed_key == ord("l"):
            print("Pressed key: f or l")
            # 現在位置を右へ移動させる。
            if map_array[current_position[0]][current_position[1] + 1] == False:
                current_position[1] += 2;
                draw_position(shared_map_array, shared_downstairs, shared_current_position)

        elif pressed_key == ord("d") or pressed_key == ord("k"):
            print("Pressed key: d or k")
            # 現在位置を下へ移動させる。
            if map_array[current_position[0] + 1][current_position[1]] == False:
                current_position[0] += 2;
                draw_position(shared_map_array, shared_downstairs, shared_current_position)

    cv2.destroyAllWindows()

