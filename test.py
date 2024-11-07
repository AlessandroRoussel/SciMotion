import moderngl
import numpy as np

ctx1 = moderngl.create_context(standalone=True)
ctx2 = moderngl.create_context(standalone=True, share=True)

width, height = 100, 100
color = np.full((width, height, 3), (255, 0, 0), dtype="u1")

with ctx1:
    texture = ctx1.texture((width, height), 3, color.tobytes())

with ctx2:
    bytes = texture.read()
    data = np.frombuffer(bytes, dtype="u1").reshape((100, 100, 3))
    print(data)