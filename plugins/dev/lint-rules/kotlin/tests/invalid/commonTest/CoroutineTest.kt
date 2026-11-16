package app
class CoroutineTest {
    fun x() = runBlocking {
        delay(1)
    }
}
