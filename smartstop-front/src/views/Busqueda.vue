<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import {
  Plane,
  User,
  Briefcase,
  Calendar,
  Plus,
  Minus,
  ChevronDown,
  MapPin,
  Search,
  Luggage,
  ArrowRightLeft,
} from "lucide-vue-next";

import AboutUs from "../components/AboutUs.vue";
import Subscription from "../components/Subscription.vue";
import { apiClient } from "../../config/api.js";

const router = useRouter();

const tripType = ref("ida-vuelta");
const showPassengerSelect = ref(false);
const passengers = ref(1);
const cabinClass = ref("Económica");

const handleTripTypeChange = () => {
  if (tripType.value === "ida") {
    returnDate.value = null;
  }
};

const cabinBags = ref([]);
const checkedBags = ref([]);

const addBag = (type) => {
  const newBag =
    type === "cabin"
      ? { height: 55, width: 35, length: 25, weight: 10 }
      : { height: 75, width: 48, length: 27, weight: 23 };
  if (type === "cabin" && cabinBags.value.length < 3)
    cabinBags.value.push(newBag);
  if (type === "checked" && checkedBags.value.length < 5)
    checkedBags.value.push(newBag);
};

const removeBag = (type) => {
  if (type === "cabin" && cabinBags.value.length > 0) cabinBags.value.pop();
  if (type === "checked" && checkedBags.value.length > 0)
    checkedBags.value.pop();
};

const originSearch = ref("");
const destSearch = ref("");
const showOriginDropdown = ref(false);
const showDestDropdown = ref(false);

const allAirports = ref([]);
const originResults = ref([]);
const destResults = ref([]);

function hideOriginDropdown() {
  window.setTimeout(() => {
    showOriginDropdown.value = false;
  }, 200);
}
function hideDestDropdown() {
  window.setTimeout(() => {
    showDestDropdown.value = false;
  }, 200);
}

const cargarAeropuertos = async () => {
  try {
    allAirports.value = await apiClient("/vuelos/aeropuertos");
  } catch (error) {
    console.error(error);
  }
};

const normalizeText = (text) =>
  text
    ? text
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
    : "";
const filterAirports = (query) => {
  if (query.length < 2) return [];
  const q = normalizeText(query);
  return allAirports.value.filter(
    (a) =>
      (a.nombre && normalizeText(a.nombre).includes(q)) ||
      (a.codigo_iata && normalizeText(a.codigo_iata).includes(q)) ||
      (a.pais && normalizeText(a.pais).includes(q)),
  );
};

const buscarOrigen = (q) => {
  originResults.value = filterAirports(q);
};
const buscarDestino = (q) => {
  destResults.value = filterAirports(q);
};
const selectOrigin = (airport) => {
  originSearch.value = `${airport.codigo_iata} - ${airport.nombre}`;
  showOriginDropdown.value = false;
};
const selectDest = (airport) => {
  destSearch.value = `${airport.codigo_iata} - ${airport.nombre}`;
  showDestDropdown.value = false;
};

const departureDate = ref(null);
const returnDate = ref(null);
const showDatePicker = ref(false);
const hoverDate = ref(null);

const todayObj = new Date();
const todayStr = `${todayObj.getFullYear()}-${String(todayObj.getMonth() + 1).padStart(2, "0")}-${String(todayObj.getDate()).padStart(2, "0")}`;
const currentMonthOffset = ref(0);

const getMonthData = (offset) => {
  const d = new Date(todayObj.getFullYear(), todayObj.getMonth() + offset, 1);
  const monthName = new Intl.DateTimeFormat("es-CL", {
    month: "long",
    year: "numeric",
  }).format(d);
  const days = [];
  const firstDay = (d.getDay() + 6) % 7;
  for (let i = 0; i < firstDay; i++) days.push({ empty: true });
  const lastDay = new Date(d.getFullYear(), d.getMonth() + 1, 0).getDate();
  for (let i = 1; i <= lastDay; i++) {
    const dateStr = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(i).padStart(2, "0")}`;
    days.push({ empty: false, day: i, dateStr });
  }
  return { title: monthName, days };
};

const month1 = computed(() => getMonthData(currentMonthOffset.value));
const month2 = computed(() => getMonthData(currentMonthOffset.value + 1));
const nextMonth = () => currentMonthOffset.value++;
const prevMonth = () => currentMonthOffset.value--;

const formatDisplayDate = (dateStr) => {
  if (!dateStr) return "";
  return new Intl.DateTimeFormat("es-CL", {
    weekday: "short",
    day: "numeric",
    month: "short",
  }).format(new Date(dateStr + "T12:00:00"));
};

const isPastDate = (dateStr) => dateStr < todayStr;
const isDateInRange = (dateStr) => {
  if (tripType.value === "ida") return false;
  if (!departureDate.value) return false;
  const end = returnDate.value || hoverDate.value;
  if (!end || isPastDate(dateStr)) return false;
  return dateStr > departureDate.value && dateStr < end;
};
const isDateSelected = (dateStr) =>
  dateStr === departureDate.value || dateStr === returnDate.value;

const handleDateClick = (dateStr) => {
  if (isPastDate(dateStr)) return;
  if (tripType.value === "ida") {
    departureDate.value = dateStr;
    returnDate.value = null;
    showDatePicker.value = false;
  } else {
    if (!departureDate.value || (departureDate.value && returnDate.value)) {
      departureDate.value = dateStr;
      returnDate.value = null;
    } else {
      if (dateStr < departureDate.value) departureDate.value = dateStr;
      else returnDate.value = dateStr;
    }
  }
};

const closeCalendarOutside = (e) => {
  const cal = document.getElementById("kayak-calendar");
  const trigger = document.getElementById("calendar-trigger");
  if (cal && !cal.contains(e.target) && trigger && !trigger.contains(e.target))
    showDatePicker.value = false;
};

onMounted(() => {
  window.addEventListener("click", closeCalendarOutside);
  cargarAeropuertos();
});

const isRedirecting = ref(false);

const ejecutarBusqueda = async () => {
  if (!originSearch.value || !destSearch.value || !departureDate.value) {
    alert("Por favor completa Origen, Destino y Fecha.");
    return;
  }
  if (tripType.value !== "ida" && !returnDate.value) {
    alert("Selecciona la fecha de regreso.");
    return;
  }

  isRedirecting.value = true;
  try {
    const maletaPrincipal =
      cabinBags.value.length > 0
        ? cabinBags.value[0]
        : checkedBags.value.length > 0
          ? checkedBags.value[0]
          : { height: 0, width: 0, length: 0, weight: 0 };
    const payload = {
      trip_type: tripType.value,
      origen_iata: originSearch.value.split("-")[0].trim().toUpperCase(),
      destino_iata: destSearch.value.split("-")[0].trim().toUpperCase(),
      fecha_salida: departureDate.value,
      fecha_regreso: tripType.value !== "ida" ? returnDate.value : null,
      passengers: parseInt(passengers.value) || 1,
      cabin_class: cabinClass.value,
      cabin_bag: cabinBags.value.length,
      checked_bag: checkedBags.value.length,
      equipaje_alto: maletaPrincipal.height,
      equipaje_ancho: maletaPrincipal.width,
      equipaje_largo: maletaPrincipal.length,
      equipaje_peso: maletaPrincipal.weight,
    };

    const resultados = await apiClient("/vuelos/buscar", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    sessionStorage.setItem("smartstop_search_params", JSON.stringify(payload));
    sessionStorage.setItem("smartstop_results", JSON.stringify(resultados));
    setTimeout(() => {
      router.push("/resultados");
    }, 600);
  } catch (error) {
    console.error("Error:", error);
    alert("Error de conexión.");
  } finally {
    isRedirecting.value = false;
  }
};
const verificarEstandarIata = (bag, type) => {
  if (!bag) return { valido: true, msg: "" };

  const medidas = [bag.height, bag.width, bag.length].sort((a, b) => b - a);
  const peso = bag.weight;

  if (type === "cabin") {
    const limites = [55, 35, 25];
    const excedeDimension = medidas.some((val, i) => val > limites[i]);
    const excedePeso = peso > 10;

    if (excedeDimension || excedePeso) {
      return {
        valido: false,
        msg: "Excede estándar cabina (Máx 55x35x25 cm, 10kg).",
      };
    }
  } else {
    const sumaMedidas =
      (bag.height || 0) + (bag.width || 0) + (bag.length || 0);
    if (sumaMedidas > 158 || peso > 23) {
      return {
        valido: false,
        msg: "Excede estándar bodega (Máx 23kg o 158cm combinados).",
      };
    }
  }
  return { valido: true, msg: "" };
};
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 w-full">
    <section
      class="relative bg-white rounded-3xl shadow-xl border border-slate-100 p-6 md:p-8 w-full z-10"
    >
      <div
        class="flex flex-wrap items-center gap-6 mb-6 pb-6 border-b border-slate-100 relative z-50"
      >
        <div class="relative group">
          <select
            v-model="tripType"
            @change="handleTripTypeChange"
            class="appearance-none bg-transparent font-bold text-slate-800 text-sm focus:outline-none cursor-pointer pr-4 hover:text-[#03254c]"
          >
            <option value="ida-vuelta">Ida y vuelta</option>
            <option value="ida">Solo ida</option>
            <option value="multidestino">Stopover</option>
          </select>
          <ChevronDown
            class="w-3.5 h-3.5 absolute right-0 top-1/2 -translate-y-1/2 pointer-events-none text-slate-500 group-hover:text-[#03254c]"
          />
        </div>

        <div class="relative group">
          <button
            @click.stop="showPassengerSelect = !showPassengerSelect"
            class="font-bold text-slate-800 text-sm flex items-center gap-1 hover:text-[#03254c]"
          >
            <User class="w-4 h-4" /> {{ passengers }}
            {{ passengers > 1 ? "pasajeros" : "pasajero" }}
            <ChevronDown class="w-3.5 h-3.5 text-slate-500" />
          </button>
          <div
            v-show="showPassengerSelect"
            class="absolute top-full left-0 mt-2 bg-white border border-slate-200 rounded-xl shadow-lg p-3 z-50 w-48"
          >
            <div class="flex items-center justify-between gap-4">
              <span class="text-xs font-bold text-slate-700">Adultos</span>
              <div class="flex items-center gap-2.5">
                <button
                  @click="passengers = Math.max(1, passengers - 1)"
                  class="w-8 h-8 rounded-lg bg-slate-100 hover:bg-slate-200 flex items-center justify-center text-slate-700"
                >
                  <Minus class="w-3.5 h-3.5" />
                </button>
                <span class="text-sm font-bold text-slate-800">{{
                  passengers
                }}</span>
                <button
                  @click="passengers = Math.min(9, passengers + 1)"
                  class="w-8 h-8 rounded-lg bg-slate-100 hover:bg-slate-200 flex items-center justify-center text-slate-700"
                >
                  <Plus class="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
            <button
              @click="showPassengerSelect = false"
              class="w-full mt-3 py-1.5 bg-slate-50 hover:bg-slate-100 text-xs font-bold text-[#03254c] rounded-md transition"
            >
              Listo
            </button>
          </div>
        </div>

        <div class="relative group">
          <select
            v-model="cabinClass"
            class="appearance-none bg-transparent font-bold text-slate-800 text-sm focus:outline-none cursor-pointer pr-4 hover:text-[#03254c]"
          >
            <option value="Económica">Económica</option>
            <option value="Premium Economy">Premium Economy</option>
            <option value="Business">Business</option>
            <option value="Primera">Primera</option>
          </select>
          <ChevronDown
            class="w-3.5 h-3.5 absolute right-0 top-1/2 -translate-y-1/2 pointer-events-none text-slate-500 group-hover:text-[#03254c]"
          />
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-2 mb-6 relative z-40">
        <div class="lg:col-span-3 relative">
          <div
            class="flex items-center border border-slate-300 rounded-t-xl lg:rounded-tr-none lg:rounded-l-xl bg-white focus-within:ring-2 ring-[#f95d3c] px-3 py-3 h-14"
          >
            <Plane class="w-5 h-5 text-slate-400 -rotate-45 shrink-0" />
            <input
              v-model="originSearch"
              @input="buscarOrigen(originSearch)"
              @focus="showOriginDropdown = true"
              @blur="hideOriginDropdown"
              placeholder="Origen"
              class="w-full bg-transparent font-bold text-slate-800 focus:outline-none pl-2 truncate"
            />
          </div>
          <div
            v-if="showOriginDropdown && originResults.length > 0"
            class="absolute top-full left-0 right-0 mt-1 bg-white border border-slate-200 shadow-xl rounded-xl z-50 overflow-hidden"
          >
            <div
              v-for="apt in originResults"
              :key="apt.codigo_iata"
              @click="selectOrigin(apt)"
              class="px-4 py-3 hover:bg-blue-50 cursor-pointer flex items-center justify-between border-b border-slate-50"
            >
              <span class="font-bold text-slate-700 text-sm truncate pr-2"
                >{{ apt.nombre }}
                <span class="text-xs font-normal text-slate-400"
                  >({{ apt.pais }})</span
                ></span
              >
              <span
                class="text-xs font-black bg-slate-100 px-2 py-1 rounded text-slate-600 shrink-0"
                >{{ apt.codigo_iata }}</span
              >
            </div>
          </div>
        </div>

        <div class="lg:col-span-3 relative">
          <div
            class="flex items-center border-x lg:border-l-0 lg:border-r border-slate-300 bg-white focus-within:ring-2 ring-[#f95d3c] px-3 py-3 h-14"
          >
            <MapPin class="w-5 h-5 text-slate-400 shrink-0" />
            <input
              v-model="destSearch"
              @input="buscarDestino(destSearch)"
              @focus="showDestDropdown = true"
              @blur="hideDestDropdown"
              placeholder="Destino Final"
              class="w-full bg-transparent font-bold text-slate-800 focus:outline-none pl-2 truncate"
            />
          </div>
          <div
            v-if="showDestDropdown && destResults.length > 0"
            class="absolute top-full left-0 right-0 mt-1 bg-white border border-slate-200 shadow-xl rounded-xl z-50 overflow-hidden"
          >
            <div
              v-for="apt in destResults"
              :key="apt.codigo_iata"
              @click="selectDest(apt)"
              class="px-4 py-3 hover:bg-blue-50 cursor-pointer flex items-center justify-between border-b border-slate-50"
            >
              <span class="font-bold text-slate-700 text-sm truncate pr-2"
                >{{ apt.nombre }}
                <span class="text-xs font-normal text-slate-400"
                  >({{ apt.pais }})</span
                ></span
              >
              <span
                class="text-xs font-black bg-slate-100 px-2 py-1 rounded text-slate-600 shrink-0"
                >{{ apt.codigo_iata }}</span
              >
            </div>
          </div>
        </div>

        <div class="lg:col-span-4 relative">
          <div
            id="calendar-trigger"
            @click.stop="showDatePicker = !showDatePicker"
            class="flex items-center border border-slate-300 bg-white hover:bg-slate-50 cursor-pointer px-4 py-3 h-14 transition-colors"
            :class="
              tripType === 'ida'
                ? 'rounded-b-xl lg:rounded-br-none lg:rounded-r-xl'
                : ''
            "
          >
            <Calendar class="w-5 h-5 text-slate-400 shrink-0" />
            <div
              class="flex items-center w-full pl-3"
              :class="{ 'divide-x divide-slate-200': tripType !== 'ida' }"
            >
              <div
                class="w-full font-bold text-slate-800 text-sm text-center truncate px-1"
                :class="{ 'text-slate-400': !departureDate }"
              >
                {{
                  departureDate ? formatDisplayDate(departureDate) : "Fecha Ida"
                }}
              </div>
              <div
                v-if="tripType !== 'ida'"
                class="w-full font-bold text-slate-800 text-sm text-center truncate px-1"
                :class="{ 'text-slate-400': !returnDate }"
              >
                {{
                  returnDate ? formatDisplayDate(returnDate) : "Fecha Vuelta"
                }}
              </div>
            </div>
          </div>

          <div
            v-if="showDatePicker"
            id="kayak-calendar"
            class="absolute top-full right-0 mt-2 bg-white rounded-2xl shadow-2xl border border-slate-200 p-6 z-50 w-full lg:w-[680px]"
          >
            <div class="flex justify-between items-center mb-6">
              <button
                @click.stop="prevMonth"
                class="p-2 hover:bg-slate-100 rounded-full transition-colors"
              >
                <ChevronDown class="w-5 h-5 rotate-90 text-slate-600" />
              </button>
              <div class="flex gap-16 md:gap-32 w-full justify-center">
                <h3
                  class="font-extrabold text-slate-800 capitalize w-32 text-center"
                >
                  {{ month1.title }}
                </h3>
                <h3
                  class="font-extrabold text-slate-800 capitalize w-32 text-center hidden md:block"
                >
                  {{ month2.title }}
                </h3>
              </div>
              <button
                @click.stop="nextMonth"
                class="p-2 hover:bg-slate-100 rounded-full transition-colors"
              >
                <ChevronDown class="w-5 h-5 -rotate-90 text-slate-600" />
              </button>
            </div>
            <div
              class="grid grid-cols-1 md:grid-cols-2 gap-8 text-center text-sm font-semibold text-slate-800"
            >
              <div>
                <div
                  class="grid grid-cols-7 gap-y-2 mb-2 text-[10px] font-black text-slate-400 uppercase tracking-wider"
                >
                  <span>Lu</span><span>Ma</span><span>Mi</span><span>Ju</span
                  ><span>Vi</span><span>Sa</span><span>Do</span>
                </div>
                <div class="grid grid-cols-7 gap-y-1 gap-x-0">
                  <div
                    v-for="(day, idx) in month1.days"
                    :key="'m1' + idx"
                    @mouseenter="
                      !isPastDate(day?.dateStr) && (hoverDate = day?.dateStr)
                    "
                    class="relative h-10 w-full flex items-center justify-center"
                  >
                    <template v-if="!day.empty">
                      <div
                        v-if="isDateInRange(day.dateStr)"
                        class="absolute inset-0 bg-blue-50/80 -z-10"
                      ></div>
                      <div
                        v-if="day.dateStr === departureDate && returnDate"
                        class="absolute inset-y-0 right-0 w-1/2 bg-blue-50/80 -z-10"
                      ></div>
                      <div
                        v-if="day.dateStr === returnDate && departureDate"
                        class="absolute inset-y-0 left-0 w-1/2 bg-blue-50/80 -z-10"
                      ></div>
                      <button
                        @click.stop="handleDateClick(day.dateStr)"
                        :disabled="isPastDate(day.dateStr)"
                        :class="[
                          'w-full h-full flex items-center justify-center transition-colors',
                          isPastDate(day.dateStr)
                            ? 'text-slate-300 cursor-not-allowed z-10'
                            : isDateSelected(day.dateStr)
                              ? 'bg-[#03254c] text-white rounded-md font-bold z-10 shadow-sm'
                              : 'hover:border hover:border-slate-300 rounded-md z-10 text-slate-700',
                        ]"
                      >
                        {{ day.day }}
                      </button>
                    </template>
                  </div>
                </div>
              </div>
              <div class="hidden md:block">
                <div
                  class="grid grid-cols-7 gap-y-2 mb-2 text-[10px] font-black text-slate-400 uppercase tracking-wider"
                >
                  <span>Lu</span><span>Ma</span><span>Mi</span><span>Ju</span
                  ><span>Vi</span><span>Sa</span><span>Do</span>
                </div>
                <div class="grid grid-cols-7 gap-y-1 gap-x-0">
                  <div
                    v-for="(day, idx) in month2.days"
                    :key="'m2' + idx"
                    @mouseenter="
                      !isPastDate(day?.dateStr) && (hoverDate = day?.dateStr)
                    "
                    class="relative h-10 w-full flex items-center justify-center"
                  >
                    <template v-if="!day.empty">
                      <div
                        v-if="isDateInRange(day.dateStr)"
                        class="absolute inset-0 bg-blue-50/80 -z-10"
                      ></div>
                      <div
                        v-if="day.dateStr === departureDate && returnDate"
                        class="absolute inset-y-0 right-0 w-1/2 bg-blue-50/80 -z-10"
                      ></div>
                      <div
                        v-if="day.dateStr === returnDate && departureDate"
                        class="absolute inset-y-0 left-0 w-1/2 bg-blue-50/80 -z-10"
                      ></div>
                      <button
                        @click.stop="handleDateClick(day.dateStr)"
                        :disabled="isPastDate(day.dateStr)"
                        :class="[
                          'w-full h-full flex items-center justify-center transition-colors',
                          isPastDate(day.dateStr)
                            ? 'text-slate-300 cursor-not-allowed z-10'
                            : isDateSelected(day.dateStr)
                              ? 'bg-[#03254c] text-white rounded-md font-bold z-10 shadow-sm'
                              : 'hover:border hover:border-slate-300 rounded-md z-10 text-slate-700',
                        ]"
                      >
                        {{ day.day }}
                      </button>
                    </template>
                  </div>
                </div>
              </div>
            </div>
            <div
              class="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between"
            >
              <button
                @click.stop="showDatePicker = false"
                class="bg-[#03254c] hover:bg-[#001c3d] text-white px-5 py-2 rounded-xl text-xs font-bold transition-all active:scale-95 ml-auto"
              >
                Aplicar
              </button>
            </div>
          </div>
        </div>

        <div class="lg:col-span-2 h-14 mt-2 lg:mt-0">
          <button
            @click="ejecutarBusqueda"
            :disabled="isRedirecting"
            class="w-full h-full bg-[#f95d3c] hover:bg-[#e04f30] disabled:bg-slate-300 disabled:cursor-not-allowed text-white rounded-xl lg:rounded-l-none font-black text-lg shadow-md active:scale-95 transition-all flex items-center justify-center gap-2"
          >
            <Search v-if="!isRedirecting" class="w-5 h-5" />
            <span
              v-if="isRedirecting"
              class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"
            ></span>
            Buscar
          </button>
        </div>
      </div>

      <div
        class="bg-blue-50/40 border border-blue-100 rounded-2xl p-6 relative z-20"
      >
        <h3
          class="text-sm font-black text-[#03254c] mb-4 flex items-center gap-2"
        >
          <Luggage class="w-5 h-5" /> Validación IATA de Equipaje
          <span class="text-xs font-normal text-slate-500">(Opcional)</span>
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <div
              class="flex items-center justify-between mb-3 border-b border-blue-200 pb-2"
            >
              <span
                class="text-xs font-bold text-slate-600 uppercase flex items-center gap-2"
                ><Briefcase class="w-4 h-4" /> En Cabina (Mano)</span
              >
              <div
                class="flex items-center gap-2 bg-white rounded-lg border shadow-sm"
              >
                <button
                  @click="removeBag('cabin')"
                  class="p-1 hover:bg-slate-100 rounded-l-lg"
                >
                  <Minus class="w-3.5 h-3.5" />
                </button>
                <span
                  class="text-xs font-black text-[#03254c] w-4 text-center"
                  >{{ cabinBags.length }}</span
                >
                <button
                  @click="addBag('cabin')"
                  class="p-1 hover:bg-slate-100 rounded-r-lg"
                >
                  <Plus class="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
            <div
              v-if="cabinBags.length === 0"
              class="text-xs text-slate-400 italic text-center py-4 bg-white/50 rounded-xl border border-dashed border-slate-200"
            >
              Sin equipaje de mano. Presiona + para agregar.
            </div>
            <div
              v-for="(bag, idx) in cabinBags"
              :key="'cab' + idx"
              class="bg-white p-3 rounded-xl border shadow-sm mb-3 animate-fade-in"
              :class="
                !verificarEstandarIata(bag, 'cabin').valido
                  ? 'border-amber-400 bg-amber-50/20'
                  : 'border-slate-200'
              "
            >
              <div class="grid grid-cols-4 gap-2">
                <div>
                  <label class="text-[10px] text-slate-500">Alto (cm)</label
                  ><input
                    v-model.number="bag.height"
                    type="number"
                    class="w-full text-xs font-bold bg-slate-50 border border-slate-200 rounded p-1 text-center"
                  />
                </div>
                <div>
                  <label class="text-[10px] text-slate-500">Ancho (cm)</label
                  ><input
                    v-model.number="bag.width"
                    type="number"
                    class="w-full text-xs font-bold bg-slate-50 border border-slate-200 rounded p-1 text-center"
                  />
                </div>
                <div>
                  <label class="text-[10px] text-slate-500">Largo (cm)</label
                  ><input
                    v-model.number="bag.length"
                    type="number"
                    class="w-full text-xs font-bold bg-slate-50 border border-slate-200 rounded p-1 text-center"
                  />
                </div>
                <div>
                  <label class="text-[10px] text-slate-500">Peso (kg)</label
                  ><input
                    v-model.number="bag.weight"
                    type="number"
                    class="w-full text-xs font-bold bg-slate-50 border border-slate-200 rounded p-1 text-center"
                  />
                </div>
              </div>
              <p
                v-if="!verificarEstandarIata(bag, 'cabin').valido"
                class="text-[10px] text-amber-700 font-medium mt-1.5"
              >
                ⚠️ {{ verificarEstandarIata(bag, "cabin").msg }}
              </p>
            </div>
          </div>
          <div>
            <div
              class="flex items-center justify-between mb-3 border-b border-blue-200 pb-2"
            >
              <span
                class="text-xs font-bold text-slate-600 uppercase flex items-center gap-2"
                ><Luggage class="w-4 h-4" /> En Bodega (Facturado)</span
              >
              <div
                class="flex items-center gap-2 bg-white rounded-lg border shadow-sm"
              >
                <button
                  @click="removeBag('checked')"
                  class="p-1 hover:bg-slate-100 rounded-l-lg"
                >
                  <Minus class="w-3.5 h-3.5" />
                </button>
                <span
                  class="text-xs font-black text-[#03254c] w-4 text-center"
                  >{{ checkedBags.length }}</span
                >
                <button
                  @click="addBag('checked')"
                  class="p-1 hover:bg-slate-100 rounded-r-lg"
                >
                  <Plus class="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
            <div
              v-if="checkedBags.length === 0"
              class="text-xs text-slate-400 italic text-center py-4 bg-white/50 rounded-xl border border-dashed border-slate-200"
            >
              Sin equipaje de bodega. Presiona + para agregar.
            </div>
            <div
              v-for="(bag, idx) in checkedBags"
              :key="'chk' + idx"
              class="bg-white p-3 rounded-xl border shadow-sm mb-3 transition-all"
              :class="
                !verificarEstandarIata(bag, 'checked').valido
                  ? 'border-amber-400 bg-amber-50/20'
                  : 'border-slate-200'
              "
            >
              <div class="grid grid-cols-4 gap-2">
                <div>
                  <label class="text-[10px] text-slate-500">Alto (cm)</label
                  ><input
                    v-model.number="bag.height"
                    type="number"
                    class="w-full text-xs font-bold bg-slate-50 border border-slate-200 rounded p-1 text-center"
                  />
                </div>
                <div>
                  <label class="text-[10px] text-slate-500">Ancho (cm)</label
                  ><input
                    v-model.number="bag.width"
                    type="number"
                    class="w-full text-xs font-bold bg-slate-50 border border-slate-200 rounded p-1 text-center"
                  />
                </div>
                <div>
                  <label class="text-[10px] text-slate-500">Largo (cm)</label
                  ><input
                    v-model.number="bag.length"
                    type="number"
                    class="w-full text-xs font-bold bg-slate-50 border border-slate-200 rounded p-1 text-center"
                  />
                </div>
                <div>
                  <label class="text-[10px] text-slate-500">Peso (kg)</label
                  ><input
                    v-model.number="bag.weight"
                    type="number"
                    class="w-full text-xs font-bold bg-slate-50 border border-slate-200 rounded p-1 text-center"
                  />
                </div>
              </div>
              <p
                v-if="!verificarEstandarIata(bag, 'checked').valido"
                class="text-[10px] text-amber-700 font-medium mt-1.5"
              >
                ⚠️ {{ verificarEstandarIata(bag, "checked").msg }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section id="acerca"><AboutUs /></section>
    <section id="suscripcion"><Subscription /></section>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-out forwards;
}
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
