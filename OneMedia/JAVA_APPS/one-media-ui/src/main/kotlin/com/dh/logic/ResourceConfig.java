package com.dh.logic;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.EnableWebMvc;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.ViewControllerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;
import org.springframework.web.servlet.resource.GzipResourceResolver;
import org.springframework.web.servlet.resource.PathResourceResolver;

@Configuration
@EnableWebMvc
public class ResourceConfig implements WebMvcConfigurer {

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        // When overriding default behavior, you need to add default(/) as well as added static paths(/webapp).

        // src/main/resources/static/...
        registry
                //.addResourceHandler("/**") // « /css/myStatic.css
                .addResourceHandler("/static/site/**") // « /static/css/myStatic.css
                .addResourceLocations("classpath:/static/site/") // Default Static Loaction
//                .setCachePeriod( 3600 )
                .resourceChain(true) // 4.1
                .addResolver(new GzipResourceResolver()) // 4.1
                .addResolver(new PathResourceResolver()); //4.1
    }

    @Override
    public void addViewControllers(ViewControllerRegistry registry) {
        registry.addRedirectViewController("/", "/static/site/index.html");
    }
}
