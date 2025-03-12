#version 330

in vec3 position;
in vec4 color;

uniform mat4 u_transform = mat4(1.0);
uniform mat4 u_view = mat4(1.0);
uniform mat4 u_projection = mat4(1.0);

out vec4 fragColor;

void main()
{
    fragColor = color;
    gl_Position = u_projection * u_view * u_transform * vec4(position, 1.0f);
}