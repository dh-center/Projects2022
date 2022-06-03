package com.dh.logic.security;

import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.util.DigestUtils;

import java.nio.charset.StandardCharsets;
import java.util.Collection;
import java.util.Collections;

public class UserPrincipal implements UserDetails {
    private final String nameInTelegram;
    private final String password;
    private final String id;

    public UserPrincipal(String nameInTelegram, String id, PasswordEncoder passwordEncoder) {
        this.nameInTelegram = nameInTelegram;
        String md5Password = getMd5Password(nameInTelegram);
        this.password = passwordEncoder.encode(md5Password);
        this.id = id;
    }

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return Collections.singletonList(new SimpleGrantedAuthority("ROLE_USER"));
    }

    @Override
    public String getPassword() {
        return password;
    }

    @Override
    public String getUsername() {
        return id;
    }

    @Override
    public boolean isAccountNonExpired() {
        return true;
    }

    @Override
    public boolean isAccountNonLocked() {
        return true;
    }

    @Override
    public boolean isCredentialsNonExpired() {
        return true;
    }

    @Override
    public boolean isEnabled() {
        return true;
    }

    private String getMd5Password(String nameInTelegram) {
        return DigestUtils.md5DigestAsHex(((nameInTelegram + "_oneMedia")
                .getBytes(StandardCharsets.UTF_8)));
    }
}
