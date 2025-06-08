# 项目结构

```
├── .env
├── .git
│   ├── COMMIT_EDITMSG
│   ├── FETCH_HEAD
│   ├── HEAD
│   ├── config
│   ├── description
│   ├── hooks
│   │   ├── applypatch-msg.sample
│   │   ├── commit-msg.sample
│   │   ├── fsmonitor-watchman.sample
│   │   ├── post-update.sample
│   │   ├── pre-applypatch.sample
│   │   ├── pre-commit.sample
│   │   ├── pre-merge-commit.sample
│   │   ├── pre-push.sample
│   │   ├── pre-rebase.sample
│   │   ├── pre-receive.sample
│   │   ├── prepare-commit-msg.sample
│   │   ├── push-to-checkout.sample
│   │   ├── sendemail-validate.sample
│   │   └── update.sample
│   ├── index
│   ├── info
│   │   └── exclude
│   ├── logs
│   │   ├── HEAD
│   │   └── refs
│   │       ├── heads
│   │       │   ├── main
│   │       │   └── person-Bailey
│   │       └── remotes
│   │           └── origin
│   │               ├── HEAD
│   │               └── person-Bailey
│   ├── objects
│   │   ├── 09
│   │   │   └── b6fa7926e9dce92c76f40decbfbf62d9245c7f
│   │   ├── 0c
│   │   │   └── 16497f2157abacd657b57d92fd5cdc777993d4
│   │   ├── 0d
│   │   │   └── 3de63f032855c898d0656380c4208c1ae9f696
│   │   ├── 15
│   │   │   ├── a2ab4e39f4088095a396269868a1d551fab139
│   │   │   └── c96be2e8f68697cca04f55b3f0ff2bd87476c8
│   │   ├── 1f
│   │   │   └── 2c21f32da02c6833f050da1bafdb2b55e4d94e
│   │   ├── 21
│   │   │   └── 90958a6d7f64e22cd844bf3de80355f9672d80
│   │   ├── 39
│   │   │   └── d51826283693672d5fc7fcfc5752c3ca6440ef
│   │   ├── 3a
│   │   │   └── f1ae00de7f7d1dd6c0fdd101b09b19098bdcdc
│   │   ├── 4c
│   │   │   └── 5788de2ee5be010c58e4e3ba9613a855f857ea
│   │   ├── 58
│   │   │   └── f3fa4d1284a3a46a9ba4e83e80fdab1fc61923
│   │   ├── 5e
│   │   │   └── c7f5302f258652d938a526c54a0efac2b62c58
│   │   ├── 5f
│   │   │   └── d688995aa8c888260b12cba642581f13a7e925
│   │   ├── 60
│   │   │   └── a433ad10c2e71d4fd4535de008cbb9e324a30b
│   │   ├── 61
│   │   │   └── bb86489a66ce765040a9a20c246b37465c7e23
│   │   ├── 68
│   │   │   └── c2206386aa9cbc0c3f7cc1444533bf668d392f
│   │   ├── 71
│   │   │   └── 2bfed2211b2ad7b15f34c6a7ff427c80304ceb
│   │   ├── 83
│   │   │   └── 368a2ae9f7e888e35a09f661f84e35cede2270
│   │   ├── 84
│   │   │   └── 95e19914e631a93d2976a9370eb966ee8d13bc
│   │   ├── 88
│   │   │   ├── 423a0132c5745728883ab35161e9b403aec4f8
│   │   │   └── b3451f77951d12043a6d278a28c0e588fe8107
│   │   ├── 89
│   │   │   └── ab7292ba406cfa7caf2b950066550a85213c49
│   │   ├── 8a
│   │   │   └── a6363799290e2ef729543e522a7bfe3b288049
│   │   ├── 8d
│   │   │   └── a04b8eb7482fdc2136f01f8bcaa30ff538fa33
│   │   ├── 8f
│   │   │   └── b0d9e3990371fd8cc07ea03fb3d8552b07a01c
│   │   ├── 91
│   │   │   └── f1cdb7d2dce6106bcabb6616e0ea79b1b4863b
│   │   ├── a0
│   │   │   └── 8d947667cf9827e90616821d833b1ebdecd123
│   │   ├── ac
│   │   │   └── 7ad71511398949d26b67418f2eb8d0d5c6d2be
│   │   ├── af
│   │   │   └── ee22c1e8f9682c8d97209eaadc429134c1dff5
│   │   ├── c1
│   │   │   └── 517772c48f75b3c46da27e034eff9cb414f471
│   │   ├── c6
│   │   │   └── 469230dbe2cd0b34a9709a5a3b853bce2be035
│   │   ├── cd
│   │   │   └── 3a6550f6c13c54bd9ee7d1dddc7349b64b4e90
│   │   ├── d2
│   │   │   ├── 24415d5303968078b47dfd19b97eeefad356d9
│   │   │   └── 60956fa5fc32e76872f454abf9861f127d8485
│   │   ├── da
│   │   │   └── da1524c98ca83c599fc7a7fdda1f8b16829475
│   │   ├── e6
│   │   │   └── 9de29bb2d1d6434b8b29ae775ad8c2e48c5391
│   │   ├── e8
│   │   │   └── c9460b8efbc9e89e7c555842d5bfbea6153caa
│   │   ├── ec
│   │   │   └── 88f0638f73edb5ef4371ca95befb1614633c94
│   │   ├── f3
│   │   │   └── dc40d24d5f473b25585bd1f9e4c683592e5f65
│   │   ├── f5
│   │   │   └── b8ed76368a534712b2fad7696a0d9064974879
│   │   ├── fe
│   │   │   └── e32fda2c479c92e7fe6ad6e3b0dcd637e30d39
│   │   ├── ff
│   │   │   ├── 9076b68cb29a09be7576c38ef1c86fc71a4654
│   │   │   └── e90c6ede301156717035306a7418a9ee791b39
│   │   ├── info
│   │   └── pack
│   │       ├── pack-0090511ef2b26ce8059f3665990922cf3fc86425.idx
│   │       ├── pack-0090511ef2b26ce8059f3665990922cf3fc86425.pack
│   │       └── pack-0090511ef2b26ce8059f3665990922cf3fc86425.rev
│   ├── packed-refs
│   └── refs
│       ├── heads
│       │   ├── main
│       │   └── person-Bailey
│       ├── remotes
│       │   └── origin
│       │       ├── HEAD
│       │       └── person-Bailey
│       └── tags
├── .idea
│   ├── .gitignore
│   ├── git_toolbox_blame.xml
│   ├── git_toolbox_prj.xml
│   ├── inspectionProfiles
│   │   ├── Project_Default.xml
│   │   └── profiles_settings.xml
│   ├── misc.xml
│   ├── modules.xml
│   ├── spring-crawler.iml
│   ├── vcs.xml
│   └── workspace.xml
├── README.md
├── __pycache__
│   └── config.cpython-311.pyc
├── config.py
├── crawler
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-311.pyc
│   │   ├── base.cpython-311.pyc
│   │   ├── spider_2jmtt.cpython-311.pyc
│   │   ├── spider_cryptotradingcafe.cpython-311.pyc
│   │   ├── spider_zhinitaimei.cpython-311.pyc
│   │   └── spyder_theblockbeats.cpython-311.pyc
│   ├── base.py
│   ├── spider_2jmtt.py
│   ├── spider_cryptotradingcafe.py
│   ├── spider_zhinitaimei.py
│   └── spyder_theblockbeats.py
├── data
│   ├── source_spider_data.article_number.json
│   └── source_spider_data.dwi_for_test_data.json
├── data_etl
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-311.pyc
│   │   └── spider_to_dwi.cpython-311.pyc
│   └── spider_to_dwi.py
├── db
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-311.pyc
│   │   └── mongo_storage.cpython-311.pyc
│   └── mongo_storage.py
├── logs
│   ├── cryptotradingcafe.log
│   ├── jmtt.log
│   ├── source_to_dwi.log
│   ├── theblockbeats.log
│   └── zhinitaimei.log
├── main.py
├── readme_create.py
├── requirements.txt
├── test.py
└── utils
    ├── __pycache__
    │   └── logger.cpython-311.pyc
    └── logger.py
```
