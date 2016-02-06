`test_autoparse`
================

It turns out that autoparse is somewhat difficult to purely unit test, because a lot of the functionality is orthogonal (typing, type deduction, argument-vs-option, flag letter assignment), but the orthogonal parts are difficult to isolate implementation and API-wise. Therefore, rather than unit-test each component with mocking so on, even though we test each orthogonal unit of functionality more or less in separate files, we understand that something failing in, say, flag letter assignment could cause a failure in type deduction tests.

In the grand scheme of things, autoparse really isn't that complicated, so hopefully a cascading test failure can be easily tracked down no matter what.
