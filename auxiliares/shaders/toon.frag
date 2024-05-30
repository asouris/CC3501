#version 330

in vec3 fragPos;
in vec3 fragNormal;

out vec4 outColor;

// Material
struct Material {
    vec3 diffuse;
    vec3 ambient;
    vec3 specular;
    float shininess;
};

uniform Material u_material;

// Lighting
uniform vec3 u_viewPos;

// Directional
struct DirectionalLight {
    vec3 direction;
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

uniform DirectionalLight u_dirLight;

// Pointlight
const int MAX_POINT_LIGHTS = 16;
uniform int u_numPointLights;

struct PointLight {
    vec3 position;
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
    float constant;
    float linear;
    float quadratic;
};

uniform PointLight u_pointLights[MAX_POINT_LIGHTS];

// Spotlight
const int MAX_SPOT_LIGHTS = 16;
uniform int u_numSpotLights;

struct SpotLight {
    vec3 position;
    vec3 direction;
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
    float constant;
    float linear;
    float quadratic;
    float cutOff;
    float outerCutOff;
};

uniform SpotLight u_spotLights[MAX_SPOT_LIGHTS];

vec3 computeDirectionalLight(vec3 normal, vec3 viewDir, DirectionalLight light) {
    //ambient
    vec3 ambient = light.ambient * u_material.ambient;

    // diffuse
    float diff = max(dot(normal, light.direction), 0.0f);
    vec3 diffuse = light.diffuse * (diff * u_material.diffuse);

    // specular blinn phong
    vec3 halfwayDir = normalize(light.direction + viewDir);
    float spec = pow(max(dot(normal, halfwayDir), 0.0f), u_material.shininess);
    vec3 specular = light.specular * (spec * u_material.specular);

    return (ambient + diffuse + specular);
}

vec3 computePointLight(vec3 normal, vec3 viewDir, PointLight light) {
    // attenuation
    vec3 lightVec = light.position - fragPos;
    float distance = length(lightVec);
    float attenuation = 1.0f / ( light.linear * distance + light.quadratic * distance * distance + light.constant );

    // ambent
    vec3 ambient = light.ambient * u_material.ambient;

    // diffiuse
    vec3 lightDir = normalize(lightVec);
    float diff = max(dot(normal, lightDir), 0.0f);
    vec3 diffuse = light.diffuse * (diff * u_material.diffuse);

    // specular blinn phong
    vec3 halfwayDir = normalize(lightDir + viewDir);
    float spec = pow(max(dot(normal, halfwayDir), 0.0f), u_material.shininess);
    vec3 specular = light.specular * (spec * u_material.specular);

    return (ambient + diffuse + specular) * attenuation;
}

vec3 computeSpotLight(vec3 normal, vec3 viewDir, SpotLight light) {
    // attenuation
    vec3 lightVec = light.position - fragPos;
    float distance = length(lightVec);
    float attenuation = 1.0f / (light.linear * distance + light.quadratic * distance * distance + light.constant);

    // ambient
    vec3 ambient = light.ambient * u_material.ambient;

    // diffuse
    vec3 lightDir = normalize(lightVec);
    float diff = max(dot(normal, lightDir), 0.0f);
    vec3 diffuse = light.diffuse * (diff * u_material.diffuse);

    // specular blinn phong
    vec3 halfwayDir = normalize(lightDir + viewDir);
    float spec = pow(max(dot(normal, halfwayDir), 0.0f), u_material.shininess);
    vec3 specular = light.specular * (spec * u_material.specular);

    // spotlight intensity
    float theta = dot(lightDir, normalize(light.direction));
    float epsilon = light.cutOff - light.outerCutOff;
    float intensity = clamp((theta - light.outerCutOff) / epsilon, 0.0f, 1.0f);

    return (ambient + diffuse + specular) * intensity * attenuation;;
}


void main()
{
    int toon_levels = 4;
    float toon_scale_factor = 1.0/toon_levels;
// DIRECTIONAL LIGHT
    //ambient
    vec3 ambient_total = u_dirLight.ambient * u_material.ambient;
    //diffuse
    vec3 normal = normalize(fragNormal);//cause interpolation post vertex shader
    float lambert = dot(normal, u_dirLight.direction);
    float diffuseFactor = floor(lambert * toon_levels) * toon_scale_factor;

    vec3 diffuse_total = u_dirLight.diffuse * (u_material.diffuse * diffuseFactor);
    //vec3 diffuse_total = u_dirLight.diffuse * (ceil(lambert*2)/2 * u_material.diffuse);
    //specular
    vec3 viewDir = normalize(u_viewPos - fragPos);
    //vec3 R = reflect(-u_dirLight.direction, normal);
    vec3 H = normalize(u_dirLight.direction + viewDir);
    float specular = max(0, dot(H, normal)) * (lambert > 0 ? 1 : 0 );

    if (specular > 0.95) specular = 0.95;
    else if (specular > 0.9) specular = 0.9;
    else specular = 0;
    //specular shininess
    float specular_exp = exp2(u_material.shininess * 8) + 2;
    vec3 specular_total = pow(specular, specular_exp) * u_dirLight.specular;

    //rim lighting
    float rimLightIntensity = dot(viewDir, normal);
    rimLightIntensity = max(0.0, 1 - rimLightIntensity);
    rimLightIntensity = smoothstep(0.59, 0.61, rimLightIntensity);
    vec3 rimLight = rimLightIntensity * diffuse_total;

    


    outColor = vec4(ambient_total + diffuse_total + rimLight, 1.0f);
    
}