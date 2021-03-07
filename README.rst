================
VirtualCrypto.py
================


.. image:: https://img.shields.io/pypi/v/virtualcrypto.svg
        :target: https://pypi.python.org/pypi/virtualcrypto

.. image:: https://img.shields.io/travis/virtualCrypto-discord/virtualcrypto.svg
        :target: https://travis-ci.com/virtualCrypto-discord/virtualcrypto

.. image:: https://readthedocs.org/projects/virtualcrypto/badge/?version=latest
        :target: https://virtualcrypto.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




VirtualCrypto Python SDK


* Free software: MIT license
* Documentation: https://virtualcrypto.readthedocs.io.

Usage
-----

Normal Usage:

.. highlight:: python

    from virtualcrypto import VirtualCryptoClient, Scope
    client = VirtualCryptoClient(
        client_id="956fcdd2-84ee-4b02-8766-8aec7dd12b05",
        client_secret="akOu2Wna3SYkVksVgaQWAEDwLmfHW1-ThIS5WQwDCfU",
        scopes=[Scope.Pay, Scope.Claim]
    )
    print(client.get_currency_by_unit("v"))
    # Currency(unit='v', guild=754191887203696731, name='vcoin', pool_amount=5000, total_amount=1000000)

For asyncio:

.. highlight:: python

    from virtualcrypto import Scope, AsyncVirtualCryptoClient
    import asyncio
    client = AsyncVirtualCryptoClient(
        client_id="956fcdd2-84ee-4b02-8766-8aec7dd12b05",
        client_secret="akOu2Wna3SYkVksVgaQWAEDwLmfHW1-ThIS5WQwDCfU",
        scopes=[Scope.Pay, Scope.Claim]
    )

    async def main():
        await client.start()
        print(await client.get_currency_by_unit("v"))
        await client.close()

    asyncio.get_event_loop().run_until_complete(main())


Features
--------

* TODO

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
