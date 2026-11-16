package app
class AssertTest {
    lateinit var repo: Repo
    fun check() = repo.find(1)!!.name
}
