-- moneyprinter
-- get some!

SLASH_MONEYPRINTER1 = "/moneyprinter"
function SlashCmdList.MONEYPRINTER(input)
  local gold, silver, copper = LibMoneyPrinter.getMoney()
  print("You have " .. gold .. "g" .. silver .. "s" .. copper .. "c.")
end
