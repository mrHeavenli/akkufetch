from string import Template

from dbus_handler import Battery
from config import Config


class Akkufetch:
    def __init__(self, dimensions: (int, int, bool) or None, battery: Battery, config: Config):
        if dimensions is None: dimensions = self._dynamic_dimensions()
        self.total_height, self.total_width, self.horizontal = dimensions
        self.height, self.width = self.total_height - 3, self.total_width - 2
        assert self.height > 0 and self.width > 0, "Battery dimensions are too small"

        self.battery = battery
        self.config = config

        self._max_charge = self.height + 1
        self.charge = int(self.battery["Percentage"] / 100 * self._max_charge)

    def _generate(self) -> [str]:
        lines = [""] * (self.total_height if self.horizontal else self.total_width)
        diode = self._get_diode_dimensions()

        if self.horizontal:
            for line in range(len(lines)):
                match line:
                    case 0: lines[line] =                           f"{' ' * diode.start}╔{ '═' * (len(diode) -1)}╗{' ' * diode.start}"
                    case 1: lines[line] =                           f"╔{'═' * (diode.start-1)}╝{self._get_horizontal_bar(line, len(diode)-1)}╚{'═' * (diode.start-1)}╗"
                    case _ if line == len(lines) - 1: lines[line] = f"╚{'═' * self.width}╝"
                    case _: lines[line] =                           f"║{self._get_horizontal_bar(line)}║"

        else:
            bar, bar_diode = self._get_vertical_bar()

            for line in range(len(lines)):
                match line:
                    case 0: lines[line] =                           f"╔{ '═' * self.height }╗ "
                    case diode.start: lines[line] =                 f"║{ bar               }╚╗"
                    case _ if line in diode: lines[line] =          f"║{ bar_diode          }║"
                    case diode.stop: lines[line] =                  f"║{ bar               }╔╝"
                    case _ if line == len(lines) - 1: lines[line] = f"╚{ '═' * self.height }╝ "
                    case _: lines[line] =                           f"║{ bar               }║ "

        return lines

    def _add_info_text(self, lines: [str]):
        format_lines = self.config["system_info.format"]
        for i in range(len(format_lines) - len(lines)): lines.append(" " * len(lines[0]))

        for i, line in enumerate(format_lines):
            template = Template(line)
            text = template.substitute({key: self.battery[key] for key in template.get_identifiers()})

            lines[i] += ' ' * self.config["system_info.indent"] + text

        return lines

    def _get_diode_dimensions(self):
        diode_size = int(self.total_width / 2)
        if (self.width % 2 == 0) ^ (diode_size % 2 == 0): diode_size += 1

        diode_start = int((self.total_width - diode_size) / 2)

        return range(diode_start, diode_start + diode_size - 1)

    def _get_vertical_bar(self):
        bar_diode = (f"{self.config['colors.charged']}"
                     f"{self.config['chars.charged'] * self.charge}"
                     f"{self.config['colors.reset']}"
                     f"{self.config['chars.empty'] * (self._max_charge - self.charge)}")

        if self.battery["State"] == 1:  # charging
            bar_diode = bar_diode[::-1].replace(self.config["chars.charged"], self.config["chars.charging"][::-1], 1)[::-1]

        if self.charge == self._max_charge: bar = bar_diode[:-len(self.config["colors.reset"])-1] + self.config["colors.reset"]
        else: bar = bar_diode[:-1]

        return bar, bar_diode

    def _get_horizontal_bar(self, line, characters=None):
        if characters is None: characters = self.width
        line -= 1  # because the first line doesn't contain a bar

        if (self._max_charge - line) == self.charge and self.battery["State"] == 1:
            return f"{self.config['colors.charged']}{self.config['chars.charging'] * characters}{self.config['colors.reset']}"
        elif (self._max_charge - line) <= self.charge:
            return f"{self.config['colors.charged']}{self.config['chars.charged'] * characters}{self.config['colors.reset']}"
        else: return self.config["chars.empty"] * characters

    def __repr__(self):
        return "\n".join(self._add_info_text(self._generate()))
