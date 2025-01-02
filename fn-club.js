/*
飞牛论坛签到
 cron "0 8 * * *" fn-club.js
*/

const axios = require("axios");
const cheerio = require("cheerio");
const notify = require("./sendNotify");

// 填写对应的 Cookie 值
const cookies = {
  pvRK_2132_saltkey: process.env.FN_KEY,
  pvRK_2132_auth: process.env.FN_AUTH,
};

const cookieHeader = Object.entries(cookies)
  .map(([key, value]) => `${key}=${value}`)
  .join("; ");

async function signIn() {
  // 随机延迟 1-2分钟
  await new Promise((resolve) =>
    setTimeout(resolve, Math.random() * 60000 + 60000)
  );
  try {
    // 签到请求链接右键打卡按钮直接复制替换
    const response = await axios.get(
      `https://club.fnnas.com/plugin.php?id=zqlj_sign&sign=${process.env.FN_SIGN}`,
      {
        headers: {
          Cookie: cookieHeader,
        },
      }
    );

    if (response.data.includes("恭喜您，打卡成功！")) {
      await notify.sendNotify("飞牛论坛", "打卡成功");
      await getSignInInfo();
    } else if (response.data.includes("您今天已经打过卡了，请勿重复操作！")) {
      await notify.sendNotify("飞牛论坛", "已经打过卡了");
    } else {
      // console.log("打卡失败, cookies可能已经过期或站点更新.");
      await notify.sendNotify(
        "飞牛论坛",
        "打卡失败, cookies可能已经过期或站点更新."
      );
    }
  } catch (error) {
    await notify.sendNotify("飞牛论坛", "打卡失败");
    // console.error("签到请求失败:", error);
  }
}

async function getSignInInfo() {
  try {
    const response = await axios.get(
      "https://club.fnnas.com/plugin.php?id=zqlj_sign",
      {
        headers: {
          Cookie: cookieHeader,
        },
      }
    );

    const $ = cheerio.load(response.data);
    const content = [];

    const patterns = [
      { name: "最近打卡", selector: 'li:contains("最近打卡")' },
      { name: "本月打卡", selector: 'li:contains("本月打卡")' },
      { name: "连续打卡", selector: 'li:contains("连续打卡")' },
      { name: "累计打卡", selector: 'li:contains("累计打卡")' },
      { name: "累计奖励", selector: 'li:contains("累计奖励")' },
      { name: "最近奖励", selector: 'li:contains("最近奖励")' },
      { name: "当前打卡等级", selector: 'li:contains("当前打卡等级")' },
    ];

    patterns.forEach((pattern) => {
      const element = $(pattern.selector).text();
      if (element) {
        content.push(`${pattern.name}: ${element.replace(/.*：/, "").trim()}`);
      }
    });

    console.log(content.join("\n"));
  } catch (error) {
    console.error("获取打卡信息失败:", error);
  }
}

signIn();
