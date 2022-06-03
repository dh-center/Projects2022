package com.dh.logic

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication


@SpringBootApplication
class CulturalApplication

fun main(args: Array<String>) {
	var context = runApplication<CulturalApplication>(*args)
	println("started!")
}

