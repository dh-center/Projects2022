package com.dh.logic.security;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.security.config.annotation.authentication.builders.AuthenticationManagerBuilder;
import org.springframework.security.config.annotation.authentication.configurers.userdetails.DaoAuthenticationConfigurer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;

@Configuration
@EnableWebSecurity
public class SecurityConfiguration extends WebSecurityConfigurerAdapter {


    protected void configure(final AuthenticationManagerBuilder auth, NamedParameterJdbcTemplate jdbcTemplate) throws Exception {
        DaoAuthenticationConfigurer<AuthenticationManagerBuilder, UserDetailsService> builder =
                auth.userDetailsService(getUserDetailsService(jdbcTemplate));
        builder.passwordEncoder(getPasswordEncoder());
    }

    @Override
    protected void configure(final HttpSecurity http) throws Exception {
        http.headers().frameOptions().sameOrigin().and()
                .csrf().disable()
                .authorizeRequests()
                .antMatchers("/admin/**").hasRole("ADMIN")
                .antMatchers("/static/site/work*").hasRole("USER")
                .antMatchers("/userQuery/**").hasRole("USER")
                .antMatchers("/anonymous*").anonymous()
                .antMatchers("/**").permitAll()
                .anyRequest().authenticated()
                .and()
                .formLogin()
                .loginPage("/static/site/login.html")
                .loginProcessingUrl("/perform_login")
                .failureUrl("/static/site/login.html?error=true")
                .and()
                .logout().logoutSuccessUrl("/static/site/login.html");
    }

    @Bean
    PasswordEncoder getPasswordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    UserDetailsService getUserDetailsService(NamedParameterJdbcTemplate jdbcTemplate) {
        return new UserPrincipalDetailsService(getPasswordEncoder(), jdbcTemplate);
    }
}
