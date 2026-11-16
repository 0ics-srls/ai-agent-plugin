package app
class Handled(private val user: User) {
    fun length(s: String?): Int = s?.length ?: 0
    fun differs(a: Int, b: Int) = a != b
    val name by lazy { user.name }
}
