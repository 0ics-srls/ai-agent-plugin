package shop

import co.touchlab.kermit.Logger

private val logger = Logger.withTag("shop")

fun report(count: Int) {
    logger.i { "loaded $count customers" }
}

fun printLabel(label: String): String = label.uppercase()
